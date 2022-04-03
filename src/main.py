import os
import pathlib

import toml
import hikari
import lightbulb

from config import Config

# if main is imported, don't run this code.
if __name__ == "__main__":
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

    path = pathlib.Path("./src/plugins")
    path = path.resolve().relative_to(pathlib.Path.cwd())
    glob = path.glob

    for ext_path in glob("[!_]*.py"):
        ext = str(ext_path.with_suffix("")).split(os.sep)[1:]
        bot.load_extensions(".".join(ext))

    bot.run(
       activity=hikari.Activity(
           name="cute transbians!",
           type=hikari.ActivityType.WATCHING,
       ),
    )
