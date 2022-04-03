import aiosqlite
import hikari
import lightbulb

plugin = lightbulb.Plugin("Example Plugin", include_datastore=True)


@plugin.listener(hikari.ShardReadyEvent)
async def ready_event(_: hikari.ShardReadyEvent) -> None:
    print("The bot is ready!")

@plugin.listener(hikari.StartingEvent, bind=True)
async def starting_event(plug: lightbulb.Plugin, _: hikari.StartingEvent) -> None:
    db = await aiosqlite.connect("ciberbot.db")
    plug.d.db = db


@plugin.command()
@lightbulb.command("ping", "Checks if the bot is alive.")
@lightbulb.implements(lightbulb.PrefixCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond("Pong!")
