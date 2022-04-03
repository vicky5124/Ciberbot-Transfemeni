import logging
import hikari
from lightbulb.ext import tasks

from src import utils, main

plugin = utils.Plugin("Notifications")


@plugin.listener(hikari.StartedEvent, bind=True)
async def start_all_tasks(plug: utils.Plugin, _: hikari.StartedEvent) -> None:
    for i in plug.bot.config.notifications:
        logging.info(i)

    #    @tasks.task(tasks.CronTrigger(i.cron), auto_start=True, wait_before_execution=True)
    #    async def cron_task() -> None:
    #        logging.warning(i.message)
    #        await plug.bot.rest.create_message(i.channel_id, i.message)

    #    cron_task.start()


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
