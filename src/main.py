from config import Config
from plugins import init

import toml
import hikari
import lightbulb

with open("Config.toml", "r", encoding="utf-8") as file:
    config = toml.load(file, Config)

bot = lightbulb.BotApp(
    token=config.discord.token,
    prefix=config.discord.prefix,
    default_enabled_guilds=config.discord.guild_ids,
)

bot.d.config = config

init.initialize_plugins(bot)

bot.run(
    activity=hikari.Activity(
        name="cute transbians!",
        type=hikari.ActivityType.WATCHING,
    ),
)
