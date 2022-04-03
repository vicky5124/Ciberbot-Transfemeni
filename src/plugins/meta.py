import aiosqlite
import hikari
import lightbulb

plugin = lightbulb.Plugin("Meta commands", include_datastore=True)


@plugin.listener(hikari.ShardReadyEvent)
async def ready_event(_: hikari.ShardReadyEvent) -> None:
    print("The bot is ready!")


@plugin.listener(hikari.StartingEvent, bind=True)
async def starting_event(plug: lightbulb.Plugin, _: hikari.StartingEvent) -> None:
    db = await aiosqlite.connect("ciberbot.db")
    plug.d.db = db


@plugin.listener(hikari.StoppingEvent, bind=True)
async def stopped_event(plug: lightbulb.Plugin, _: hikari.StoppingEvent) -> None:
    await plug.d.db.close()


@plugin.command()
@lightbulb.command("ping", "Checks if the bot is alive.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond("Pong!")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
