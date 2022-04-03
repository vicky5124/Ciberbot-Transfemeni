import logging
import hikari

from src import utils, main
from src.plugins.eval import eval_python

plugin = utils.Plugin("Notifications")


@plugin.listener(hikari.StartedEvent, bind=True)
async def start_all_tasks(plug: utils.Plugin, _: hikari.StartedEvent) -> None:
    for i in plug.bot.config.notifications:
        logging.info(i)

        await eval_python(
            plug.bot,
            f"""
            from lightbulb.ext import tasks

            @tasks.task(tasks.CronTrigger("{i.cron}"), auto_start=True, wait_before_execution=True)
            async def cron_task() -> None:
                logging.warning("{i.message}")
                await bot.rest.create_message({i.channel_id}, "{i.message}")

            cron_task.start()
            """,
        )


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
