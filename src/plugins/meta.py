import logging
import hikari
import lightbulb
from cassandra.cluster import (
    Cluster,
    ExecutionProfile,
    EXEC_PROFILE_DEFAULT,
    Session,
)
from cassandra.query import named_tuple_factory, dict_factory
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy

from src import utils, main, migrations, config
from src.cassandra_async_session import load_asyncio_to_session

plugin = utils.Plugin("Meta commands")


def start_database(config: config.ConfigCassandra) -> Session:
    tuple_profile = ExecutionProfile(
        request_timeout=10,
        row_factory=named_tuple_factory,
        load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy()),
    )
    dict_profile = ExecutionProfile(
        request_timeout=10,
        row_factory=dict_factory,
        load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy()),
    )

    profiles = {EXEC_PROFILE_DEFAULT: tuple_profile, "dict": dict_profile}

    cluster = Cluster(
        contact_points=config.hosts,
        port=config.port,
        execution_profiles=profiles,
        protocol_version=4,
    )
    return load_asyncio_to_session(cluster.connect())


@plugin.listener(hikari.ShardReadyEvent)
async def ready_event(_: hikari.ShardReadyEvent) -> None:
    logging.info("The bot is ready!")


@plugin.listener(hikari.StartingEvent, bind=True)
async def starting_event(plug: utils.Plugin, _: hikari.StartingEvent) -> None:
    plug.bot.db = start_database(plug.bot.config.cassandra)

    await plug.bot.db.execute_asyncio(
        f"""
        CREATE KEYSPACE IF NOT EXISTS {plug.bot.config.cassandra.keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1' }}
        """
    )

    await plug.bot.db.set_keyspace_asyncio(plug.bot.config.cassandra.keyspace)

    await migrations.run_migrations(plug.bot.db)


@plugin.listener(hikari.StoppingEvent, bind=True)
async def stopped_event(plug: utils.Plugin, _: hikari.StoppingEvent) -> None:
    # plug.bot.db.shutdown()
    pass


@plugin.command()
@lightbulb.command("ping", "Checks if the bot is alive.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: utils.Context) -> None:
    await ctx.respond("Pong!")


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
