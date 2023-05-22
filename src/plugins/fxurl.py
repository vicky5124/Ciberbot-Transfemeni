import re
import typing as t
from urllib.parse import urlparse

import hikari
from hikari.messages import MessageFlag

from src import utils, main

plugin = utils.Plugin("FX URLs")


#URL_REGEX = r"""((?:(?:https|ftp|http)?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|org|es|cat|net)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|uk|ac)\b/?(?!@)))"""
#Simplified Regex to only care about .com and .net and http and https, also escaped /
URL_REGEX = r"""((?:(?:https|http)?:(?:\/{1,3}|[\w%])|[\w.\-]+[.](?:com|net)\/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[\w]+(?:[.\-][a-z0-9]+)*[.](?:com|net)\b\/?(?!@)))"""

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

    fx_url= ""

    for idx, i in enumerate(urls):
        url = urlparse(i)
        if "twitter.com" == url.hostname or "www.twitter.com" == url.hostname or "mobile.twitter.com" == url.hostname:
            #msg_to_send += f"[Link {idx}](https://fxtwitter.com{url.path}) "
            fx_url += f"https://fxtwitter.com{url.path}\n"
        if "pixiv.net" == url.hostname or "www.pixiv.net" == url.hostname:
            #msg_to_send += f"[Link {idx}](https://fxpixiv.net{url.path}) "
            fx_url += f"https://fxpixiv.net{url.path}\n"

    # If the message had URLs that werent twitter or pixiv, skip the fixing.
    if fx_url:
        await msg.edit(flags=MessageFlag.SUPPRESS_EMBEDS)
        await msg.respond(fx_url, reply=True)


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
