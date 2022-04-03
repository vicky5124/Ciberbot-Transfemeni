import lightbulb

from plugins.meta import plugin as meta


def initialize_plugins(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(meta)
