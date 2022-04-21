import os
import re
import hashlib
import logging
import typing as t

import aiofiles
import aiosqlite


async def init_table(db: aiosqlite.Connection) -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS __migrations (
            id INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            checksum TEXT NOT NULL
        )
        """
    )

    await db.commit()


async def get_checksum(filename: str) -> str:
    async with aiofiles.open(filename, "r") as f:
        content = await f.read()
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def get_physical_migrations() -> t.Dict[int, t.Tuple[str, str, str]]:
    valid_file_re = re.compile(r"^(\d+)-(.+)\.sql$")
    all_filenames = os.listdir("migrations")
    valid_files = [f for f in all_filenames if valid_file_re.match(f)]

    checksums = []

    for filename in valid_files:
        checksum = await get_checksum(f"migrations/{filename}")
        checksums.append(checksum)

    parsed_files = []

    for file in valid_files:
        split = file.split("-")
        version = int(split[0])
        description = split[1][:-4]
        parsed_files.append((version, description))

    values = [
        (int(f[0]), f[1], checksums[idx], valid_files[idx])
        for idx, f in enumerate(parsed_files)
    ]
    values.sort(key=lambda x: x[0])

    return {v[0]: (v[1], v[2], v[3]) for v in values}


async def validate_existing_migrations(
    db: aiosqlite.Connection, physical_migrations: t.Dict[int, t.Tuple[str, str, str]]
) -> bool:
    async with db.execute("SELECT * FROM __migrations") as cursor:
        database_migrations = await cursor.fetchall()

    for db_migration in database_migrations:
        if db_migration[0] in physical_migrations.keys():
            if db_migration[2] != physical_migrations[db_migration[0]][1]:
                logging.error(
                    f"Migration {db_migration[0]} {db_migration[1]} has been modified since applied"
                )
                return False
            else:
                logging.info(
                    f"Migration '{db_migration[0]} - {db_migration[1]}' already applied and is valid"
                )
                del physical_migrations[db_migration[0]]
        else:
            logging.error(
                f"Migration {db_migration[0]} {db_migration[1]} has been removed since applied"
            )
            return False

    for ph_migration in physical_migrations.items():
        logging.warning(
            f"Migration '{ph_migration[0]} - {ph_migration[1][0]}' is not applied yet"
        )

    return True


async def apply_migrations(
    db: aiosqlite.Connection, physical_migrations: t.Dict[int, t.Tuple[str, str, str]]
) -> None:
    for (ph_migration_id, ph_migration) in physical_migrations.items():
        logging.info(f"Applying migration '{ph_migration_id} - {ph_migration[0]}'")

        async with aiofiles.open(f"migrations/{ph_migration[2]}", "r") as f:
            content = await f.read()
            await db.executescript(content)

        await db.execute(
            "INSERT INTO __migrations (id, description, checksum) VALUES (?, ?, ?)",
            (
                ph_migration_id,
                ph_migration[0],
                ph_migration[1],
            ),
        )

        await db.commit()

        logging.info(f"Migration {ph_migration_id} applied")
