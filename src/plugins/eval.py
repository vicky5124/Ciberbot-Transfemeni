import asyncio
import io
import sys
import logging
import textwrap
import traceback
import typing as t
from contextlib import redirect_stdout

import hikari
import lightbulb
from lightbulb.commands.base import OptionModifier

import src
from src import utils, main

plugin = lightbulb.Plugin("Meta commands")


def eprint(*args: t.Any, **kwargs: t.Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


async def eval_python(ctx: t.Union[utils.Context, main.CiberBot], code: str) -> None:
    should_reply = True
    env: t.Any = {}

    if isinstance(ctx, lightbulb.BotApp):
        should_reply = False

        env["src"] = src
        env["bot"] = ctx
        env["app"] = ctx
        env["eprint"] = eprint

    elif isinstance(ctx, lightbulb.Context):
        assert isinstance(ctx.event, hikari.MessageCreateEvent)

        env["src"] = src
        env["bot"] = ctx.bot
        env["app"] = ctx.bot
        env["eprint"] = eprint
        env["src"] = src
        env["ctx"] = ctx
        env["bot"] = ctx.bot
        env["app"] = ctx.bot
        env["msg"] = ctx.event.message
        env["message"] = ctx.event.message
        env["server_id"] = ctx.guild_id
        env["guild_id"] = ctx.guild_id
        env["channel_id"] = ctx.channel_id
        env["user_id"] = ctx.author.id
        env["author_id"] = ctx.author.id
        env["author"] = ctx.author
        env["eprint"] = eprint

    env.update(globals())
    stdout = io.StringIO()

    new_forced_async_code = f"async def code():\n{textwrap.indent(code, '    ')}"

    try:
        logging.debug("Preparing eval.")
        exec(new_forced_async_code, env)
    except Exception as error:
        if should_reply:
            assert isinstance(ctx, lightbulb.Context)
            assert isinstance(ctx.event, hikari.MessageCreateEvent)

            embed = hikari.Embed(
                title="Failed to execute.",
                description=f"{error} ```py\n{traceback.format_exc()}\n```\n```py\n{error.__class__.__name__}\n```",
                colour=(255, 10, 40),
            )

            await ctx.respond(embed=embed)
            await ctx.event.message.add_reaction("❌")
        else:
            logging.error(error)
            logging.error(traceback.format_exc())
            logging.error(error.__class__.__name__)

        return

    code_function: t.Any = env["code"]

    try:
        logging.debug("Running eval.")
        with redirect_stdout(stdout):
            if isinstance(ctx, lightbulb.Context):
                result = await asyncio.wait_for(
                    code_function(), timeout=ctx.bot.config.commands.eval_timeout
                )
            else:
                result = await asyncio.wait_for(
                    code_function(), timeout=ctx.config.commands.eval_timeout
                )
    except asyncio.TimeoutError:
        value = stdout.getvalue()

        if should_reply:
            assert isinstance(ctx, lightbulb.Context)
            assert isinstance(ctx.event, hikari.MessageCreateEvent)

            embed = hikari.Embed(
                title="The code took too long to execute.",
                description=f"Standard Output: ```py\n{value}\n```",
                colour=(168, 80, 100),
            )

            await ctx.respond(embed=embed)
            await ctx.event.message.add_reaction("❌")
        else:
            logging.error("The code took too long to execute.")
            logging.error(f"Standard Output: {value}")

        return
    except Exception as error:
        value = stdout.getvalue()

        if should_reply:
            assert isinstance(ctx, lightbulb.Context)
            assert isinstance(ctx.event, hikari.MessageCreateEvent)

            embed = hikari.Embed(
                title="Failed to execute.",
                description=f"{error} ```py\n{traceback.format_exc()}\n```\n```py\n{value}\n```",
                colour=(255, 10, 40),
            )

            await ctx.respond(embed=embed)
            await ctx.event.message.add_reaction("❌")
        else:
            logging.error(error)
            logging.error(traceback.format_exc())
            logging.error(value)

        return

    logging.debug("Finishing eval.")

    if should_reply:
        assert isinstance(ctx, lightbulb.Context)
        assert isinstance(ctx.event, hikari.MessageCreateEvent)

        value = stdout.getvalue()

        embed = hikari.Embed(
            title="Success!",
            description=f"Returned value: ```py\n{result}\n```\nStandard Output: ```py\n{value}\n```",
            colour=(5, 255, 70),
        )

        await ctx.respond(embed=embed)
        await ctx.event.message.add_reaction("✅")


@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(
    "raw_source", "source code to run", modifier=OptionModifier.CONSUME_REST
)
@lightbulb.command(
    "admin_eval", "Evaluates python code.", hidden=True, aliases=["eval"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def admin_eval(ctx: utils.Context) -> None:
    code = ctx.options.raw_source

    logging.warning("Running eval command.")
    logging.warning(code)

    if code.startswith("```") and code.endswith("\n```"):
        code = "\n".join(code.split("\n")[1:-1])
    else:
        code = code.strip("` \n")

    await eval_python(ctx, code)


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
