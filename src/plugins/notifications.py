import functools
import logging

import hikari
from lightbulb.ext import tasks

from src import utils, main, config

plugin = utils.Plugin("Notifications")


@plugin.listener(hikari.StartedEvent, bind=True)
async def start_all_tasks(plug: utils.Plugin, _: hikari.StartedEvent) -> None:
    async def cron_task(item: config.ConfigNotifications) -> None:
        logging.debug(item.message)
        await plug.bot.rest.create_message(item.channel_id, item.message)

    for i in plug.bot.config.notifications:
        logging.info(f"Starting task for:\n{i.message}")

        func = functools.partial(cron_task, i)

        tsk = tasks.task(tasks.CronTrigger(i.cron), wait_before_execution=True)(func)
        tsk.start()


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
