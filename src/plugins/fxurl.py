import re
import typing as t
from urllib.parse import urlparse

import hikari
from hikari.messages import MessageFlag

from src import utils, main

plugin = utils.Plugin("FX URLs")


URL_REGEX = r"""((?:(?:https|ftp|http)?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|org|es|cat|net)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|uk|ac)\b/?(?!@)))"""


@plugin.listener(hikari.MessageCreateEvent)  # type: ignore
async def on_message(event: hikari.MessageCreateEvent) -> None:
    msg = event.message

    # Check if the message content is not empty nor None, so the regex expression works.
    if not msg.content:
        return

    urls: t.List[str] = re.findall(URL_REGEX, msg.content)

    # Check if there's URLs in the message.
    if not urls:
        return

    msg_to_send = ""

    for i in urls:
        url = urlparse(i)
        if "twitter" in url.netloc and "fx" not in url.netloc:
            msg_to_send += f"https://fxtwitter.com{url.path} "
        if "pixiv" in url.netloc and "fx" not in url.netloc:
            msg_to_send += f"https://fxpixiv.net{url.path} "

    # If the message had URLs that werent twitter or pixiv, skip the fixing.
    if msg_to_send:
        msg_to_send = f"He torbat contingut que es veu incorrectament en Discord i l'he corregit!\n{msg_to_send}"
        await msg.edit(flags=MessageFlag.SUPPRESS_EMBEDS)
        await msg.respond(msg_to_send, reply=True)


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
