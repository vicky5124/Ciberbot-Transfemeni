import typing as t
from src.uwuri_parser import uwuriparser
from urllib.parse import urlparse

import hikari
from hikari.messages import MessageFlag

from src import utils, main

plugin = utils.Plugin("FX URLs")

@plugin.listener(hikari.MessageCreateEvent)  # type: ignore
async def on_message(event: hikari.MessageCreateEvent) -> None:
    msg = event.message

    # Check if the message content is not empty nor None, so the parser works.
    if not msg.content:
        return

    urls: t.List[str] = uwuriparser(msg.content)

    # Check if there's URLs in the message.
    if not urls:
        return

    fx_url = ""

    for idx, i in enumerate(urls):
        url = urlparse(i)
        if url.hostname in {"twitter.com", "www.twitter.com", "mobile.twitter.com"}:
            fx_url += f"https://fxtwitter.com{url.path}\n"
        if url.hostname in {"pixiv.net", "www.pixiv.net"}:
            fx_url += f"https://fxpixiv.net{url.path}\n"

    # If the message had URLs that weren't twitter or pixiv, skip the fixing.
    if fx_url:
        await msg.edit(flags=MessageFlag.SUPPRESS_EMBEDS)
        await msg.respond(fx_url, reply=True)


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)