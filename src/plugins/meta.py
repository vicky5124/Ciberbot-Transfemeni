import logging

import aiosqlite
import hikari
import lightbulb

from src import utils, main, migrations

plugin = utils.Plugin("Meta commands")


@plugin.listener(hikari.ShardReadyEvent)
async def ready_event(_: hikari.ShardReadyEvent) -> None:
    logging.info("The bot is ready!")


@plugin.listener(hikari.StartingEvent, bind=True)
async def starting_event(plug: utils.Plugin, _: hikari.StartingEvent) -> None:
    db = await aiosqlite.connect("ciberbot.db")
    plug.bot.db = db

    await migrations.init_table(db)

    physical_migrations = await migrations.get_physical_migrations()
    if await migrations.validate_existing_migrations(db, physical_migrations):
        await migrations.apply_migrations(db, physical_migrations)


@plugin.listener(hikari.StoppingEvent, bind=True)
async def stopped_event(plug: utils.Plugin, _: hikari.StoppingEvent) -> None:
    await plug.bot.db.close()


@plugin.command()
@lightbulb.command("ping", "Checks if the bot is alive.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: utils.Context) -> None:
    await ctx.respond("Pong!")


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
