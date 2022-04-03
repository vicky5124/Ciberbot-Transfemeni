import os

import toml
import hikari
import lightbulb

from src.config import Config


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    with open("Config.toml", "r", encoding="utf-8") as file:
        config = toml.load(file, Config)

    bot = lightbulb.BotApp(
        token=config.discord.token,
        prefix=config.discord.prefix,
        default_enabled_guilds=config.discord.guild_ids,
        intents=hikari.Intents.GUILD_MESSAGES,
    )

    bot.d.config = config

    bot.load_extensions_from("./src/plugins")

    bot.run(
        activity=hikari.Activity(
            name="cute transbians!",
            type=hikari.ActivityType.WATCHING,
        ),
    )
