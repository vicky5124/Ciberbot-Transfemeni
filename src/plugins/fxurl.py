import asyncio
import re
import typing as t
from urllib.parse import urlparse, quote, unquote

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


TWITTER_HOSTS = {
    "twitter.com",
    "www.twitter.com",
    "m.twitter.com",
    "mobile.twitter.com",
}

PIXIV_HOSTS = {
    "pixiv.net",
    "www.pixiv.net",
    "m.pixiv.net",
}


@plugin.listener(hikari.MessageCreateEvent)  # type: ignore
async def on_message(event: hikari.MessageCreateEvent) -> None:
    msg = event.message
    ast = parse(msg.content)

    msg_to_send = ""

    for i in collect_previewing_links(ast):
        url = urlparse(i)
        if url.scheme.lower() not in {"http", "https"}:
            continue
        host = quote(unquote(url.netloc).lower())
        path = quote(unquote(url.path))
        if host in TWITTER_HOSTS:
            if re.fullmatch(r"/[^/]+/status/\d+(?:/photo/\d+)?", path.lower()):
                msg_to_send += f"https://fxtwitter.com{path} "
        if host in PIXIV_HOSTS:
            msg_to_send += f"https://fxpixiv.net{path} "

    # If the message had URLs that werent twitter or pixiv, skip the fixing.
    if msg_to_send:
        await msg.respond(msg_to_send, reply=True)
        await mark_for_embed_suppression(msg)


@plugin.listener(hikari.MessageUpdateEvent)  # type: ignore
async def on_message_updated(event: hikari.MessageUpdateEvent) -> None:
    await check_embed_suppression(event.message)


# Discord clients have a race condition where, if the SUPPRESS_EMBEDS flag update
# arrives *before* the embeds arrive, they will be shown regardless (until client
# restarts or channel messages are re-rendered). To work around this, wait for the
# embed(s) to appear before applying the flag.

embed_suppression_pending: t.Set[int] = set()

async def mark_for_embed_suppression(msg: hikari.Message) -> None:
    assert msg.id not in embed_suppression_pending
    embed_suppression_pending.add(msg.id)

    # start a timeout, just in case (some) embeds never arrive
    asyncio.create_task(embed_suppression_timeout_task(msg))

    # check to see if embeds have already appeared (can happen if they were cached),
    # and we can suppress them right away
    await check_embed_suppression(msg)

async def check_embed_suppression(msg: hikari.PartialMessage) -> None:
    # if this is a marked message and embeds have arrived, suppress them
    if msg.embeds and msg.id in embed_suppression_pending:
        embed_suppression_pending.remove(msg.id)
        await msg.edit(flags=MessageFlag.SUPPRESS_EMBEDS)

async def embed_suppression_timeout_task(msg: hikari.Message) -> None:
    await asyncio.sleep(10)

    # if the message is still marked, suppress embeds now
    if msg.id in embed_suppression_pending:
        embed_suppression_pending.remove(msg.id)
        await msg.edit(flags=MessageFlag.SUPPRESS_EMBEDS)


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
