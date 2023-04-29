import os
import re
import sys
import hashlib
import logging
import traceback
import typing as t
from collections import defaultdict

import aiofiles
from src.cassandra_async_session import AsyncioSession


async def init_table(db: AsyncioSession) -> None:
    await db.execute_asyncio(
        """
        CREATE TABLE IF NOT EXISTS priv_migration (
            id INT,
            description TEXT,
            checksum TEXT,
            PRIMARY KEY (id)
        )
        """
    )


async def get_checksum(filename: str) -> str:
    async with aiofiles.open(filename, "r") as f:
        content = await f.read()
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def run_migrations(db: AsyncioSession) -> None:
    await init_table(db)

    physical_migrations = await get_physical_migrations()
    if await validate_existing_migrations(db, physical_migrations):
        await apply_migrations(db, physical_migrations)


async def get_physical_migrations() -> t.Dict[int, t.Tuple[str, str, str]]:
    valid_file_re = re.compile(r"^(\d+)-(.+)\.cql$")
    groups = defaultdict(list)

    for filename in os.listdir("migrations"):
        if m := valid_file_re.match(filename):
            version, description = m.groups()
            checksum = await get_checksum(f"migrations/{filename}")
            entry = int(version), (description, checksum, filename)
            groups[description == "drop"].append(entry)

    return dict(sorted(groups[False]))


async def validate_existing_migrations(
    db: AsyncioSession, physical_migrations: t.Dict[int, t.Tuple[str, str, str]]
) -> bool:
    database_migrations = await db.execute_asyncio("SELECT * FROM priv_migration")

    for db_migration in database_migrations:
        if db_migration.id in physical_migrations.keys():
            if db_migration.checksum != physical_migrations[db_migration[0]][1]:
                logging.error(
                    f"Migration {db_migration.id} {db_migration.description} has been modified since applied"
                )
                return False
            else:
                logging.info(
                    f"Migration '{db_migration.id} - {db_migration.description}' already applied and is valid"
                )
                del physical_migrations[db_migration.id]
        else:
            logging.error(
                f"Migration {db_migration.id} {db_migration.description} has been removed since applied"
            )
            return False

    for ph_migration in physical_migrations.items():
        logging.warning(
            f"Migration '{ph_migration[0]} - {ph_migration[1][0]}' is not applied yet"
        )

    return True


async def apply_migrations(
    db: AsyncioSession, physical_migrations: t.Dict[int, t.Tuple[str, str, str]]
) -> None:
    for ph_migration_id, ph_migration in physical_migrations.items():
        logging.info(f"Applying migration '{ph_migration_id} - {ph_migration[0]}'")

        async with aiofiles.open(f"migrations/{ph_migration[2]}", "r") as f:
            content = await f.read()
            should_continue = False
            for i in content.split(";"):
                i = i.strip()
                if i:
                    try:
                        await db.execute_asyncio(i)
                    except Exception as e:
                        logging.error(
                            f"Error applying migration {ph_migration_id} - {ph_migration[0]}, calling drop."
                        )
                        await drop_migration_by_id(db, ph_migration_id, True)
                        traceback.print_exception(
                            type(e), e, e.__traceback__, file=sys.stderr
                        )
                        should_continue = True

            if should_continue:
                continue

        await db.execute_asyncio(
            "INSERT INTO priv_migration (id, description, checksum) VALUES (%s, %s, %s)",
            (
                ph_migration_id,
                ph_migration[0],
                ph_migration[1],
            ),
        )

        logging.info(f"Migration {ph_migration_id} applied")


async def drop_migration_by_id(
    db: AsyncioSession, id: int, skip_check: bool = False
) -> None:
    if not skip_check:
        row = await db.execute_asyncio(
            "SELECT * FROM priv_migration WHERE id = %s", (id,)
        )

        migration = row.one()

        if not migration:
            logging.error(f"The migration with the ID {id} has not been applied")
            return

        logging.info(f"Dropping migration '{migration.id} - {migration.description}'")
    else:
        logging.warning(f"Dropping migration '{id}'")

    async with aiofiles.open(f"migrations/{id}-drop.cql", "r") as f:
        content = await f.read()
        await db.execute_asyncio(content)

    if not skip_check:
        await db.execute_asyncio(
            "DELETE FROM priv_migration WHERE id = %s",
            (id,),
        )

    logging.info(f"Migration {id} dropped")
