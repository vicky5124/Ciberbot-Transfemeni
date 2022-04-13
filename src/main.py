import os

import toml
import hikari
import aiosqlite
import lightbulb
from lightbulb.ext import tasks

from src.config import Config


class CiberBot(lightbulb.BotApp):
    __slots__ = ("db", "config")

    def __init__(self) -> None:
        with open("Config.toml", "r", encoding="utf-8") as file:
            config = toml.load(file, Config)

        super().__init__(
            token=config.discord.token,
            prefix=config.discord.prefix,
            default_enabled_guilds=config.discord.guild_ids,
            intents=hikari.Intents.ALL_MESSAGES
            | hikari.Intents.GUILDS
            | hikari.Intents.MESSAGE_CONTENT
            | hikari.Intents.GUILD_MESSAGE_REACTIONS,
        )

        self.config: Config = config
        self.db: aiosqlite.Connection
        self.load_extensions_from("./src/plugins")


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot = CiberBot()
    tasks.load(bot)

    bot.run(
        activity=hikari.Activity(
            name="cute transbians!",
            type=hikari.ActivityType.WATCHING,
        ),
    )
