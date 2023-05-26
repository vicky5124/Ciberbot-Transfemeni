import asyncio
import re
import typing as t
from urllib.parse import urlparse

import hikari
from hikari.messages import MessageFlag

from discord_markdown_ast_parser import parse
from discord_markdown_ast_parser.parser import Node, NodeType

from src import utils, main

plugin = utils.Plugin("FX URLs")


def collect_previewing_links(ast: t.List[Node]) -> t.Iterator[str]:
    def visit(node: Node) -> t.Iterator[str]:
        # don't descend into spoilers
        if node.node_type == NodeType.SPOILER:
            return

        if node.node_type == NodeType.URL_WITH_PREVIEW:
            assert node.url
            yield node.url

        for node in node.children or []:
            yield from visit(node)

    for node in ast:
        yield from visit(node)


@plugin.listener(hikari.MessageCreateEvent)  # type: ignore
async def on_message(event: hikari.MessageCreateEvent) -> None:
    msg = event.message
    ast = parse(msg.content)

    msg_to_send = ""

    for i in collect_previewing_links(ast):
        url = urlparse(i)
        if (
            "twitter" in url.netloc
            and "fx" not in url.netloc
            and "vx" not in url.netloc
        ):
            # msg_to_send += f"[Link {idx}](https://fxtwitter.com{url.path}) "
            msg_to_send += f"https://fxtwitter.com{url.path} "
        if "pixiv" in url.netloc and "fx" not in url.netloc:
            # msg_to_send += f"[Link {idx}](https://fxpixiv.net{url.path}) "
            msg_to_send += f"https://fxpixiv.net{url.path} "

    # If the message had URLs that werent twitter or pixiv, skip the fixing.
    if msg_to_send:
        await msg.respond(msg_to_send, reply=True)
        # The embed in the original message may be delayed. Supress it after the timeout.
        await asyncio.sleep(10)
        await msg.edit(flags=MessageFlag.SUPPRESS_EMBEDS)


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
