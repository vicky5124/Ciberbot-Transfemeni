import random
import functools
import logging
import typing as t
from pprint import pprint

import hikari
from lightbulb.ext import tasks

from src import utils, main, config

plugin = utils.Plugin("Notifications", include_datastore=True)


@plugin.listener(hikari.StartedEvent, bind=True)
async def start_all_tasks(plug: utils.Plugin, _: hikari.StartedEvent) -> None:
    async def cron_task(item: config.ConfigNotifications) -> None:
        probability = t.cast(float, getattr(item, "probability", None))
        if probability != None:
            if not (random.random() < probability):
                return

        logging.debug(item.message)
        await plug.bot.rest.create_message(
            item.channel_id,
            item.message,
            mentions_everyone=True,
            role_mentions=True,
            user_mentions=True,
        )

    for i in plug.bot.config.notifications:
        logging.info(f"Starting task for:\n{i.message}")

        func = functools.partial(cron_task, i)

        tsk = tasks.task(tasks.CronTrigger(i.cron), wait_before_execution=True)(func)
        tsk.start()


@plugin.listener(hikari.StartingEvent, bind=True)
async def load_welcome_channels(plug: utils.Plugin, _: hikari.StartingEvent) -> None:
    welcome_config = plug.bot.config.welcome

    welcome: t.Dict[int, config.ConfigWelcome] = {}

    logging.info("Loading welcome channels")

    for i in welcome_config.values():
        welcome[i.guild_id] = i

    plug.d.welcome = welcome


@plugin.listener(hikari.MemberCreateEvent, bind=True)
async def welcome_message(plug: utils.Plugin, event: hikari.MemberCreateEvent) -> None:
    config = plug.d.welcome.get(event.guild_id)

    if not config:
        return

    heading = random.choice(config.headings).replace("%u", f"<@!{event.user_id}>")
    msg = f"{heading}\n\n{config.message}"

    await plug.bot.rest.create_message(
        config.channel_id, msg, user_mentions=[event.user_id]
    )


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
