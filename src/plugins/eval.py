import asyncio
import io
import sys
import types
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


async def eval_python(ctx: utils.Context, code: str, should_reply: bool) -> None:
    if not isinstance(ctx.event, hikari.MessageCreateEvent):
        return

    env: t.Dict[
        str,
        t.Union[
            types.ModuleType,  # src
            utils.Context,  # ctx
            main.CiberBot,  # bot, app
            hikari.Message,  # msg, message
            t.Optional[int],  # server_id, guild_id
            int,  # channel_id, user_id, author_id
            hikari.User,  # author
            t.Callable[[t.Any, t.Any], None],  # eprint
            t.Any,  # code
        ],
    ] = {
        "src": src,
        "ctx": ctx,
        "bot": ctx.bot,
        "app": ctx.bot,
        "msg": ctx.event.message,
        "message": ctx.event.message,
        "server_id": ctx.guild_id,
        "guild_id": ctx.guild_id,
        "channel_id": ctx.channel_id,
        "user_id": ctx.author.id,
        "author_id": ctx.author.id,
        "author": ctx.author,
        "eprint": eprint,
    }

    env.update(globals())
    stdout = io.StringIO()

    new_forced_async_code = f"async def code():\n{textwrap.indent(code, '    ')}"

    try:
        logging.debug("Preparing eval.")
        exec(new_forced_async_code, env)
    except Exception as error:
        if should_reply:
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
            result = await asyncio.wait_for(
                code_function(), timeout=ctx.bot.config.commands.eval_timeout
            )
    except asyncio.TimeoutError:
        value = stdout.getvalue()

        if should_reply:
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

    await eval_python(ctx, code, True)


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
