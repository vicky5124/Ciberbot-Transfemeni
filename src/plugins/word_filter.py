import re
import typing as t

import hikari
from text_unidecode import unidecode

from src import utils, main

plugin = utils.Plugin("FX URLs")


@plugin.listener(hikari.MessageCreateEvent)  # type: ignore
async def on_message_create(event: hikari.MessageCreateEvent) -> None:
    msg = event.message

    if not msg.content:
        return


@plugin.listener(hikari.MessageUpdateEvent)  # type: ignore
async def on_message_edit(event: hikari.MessageUpdateEvent) -> None:
    msg = event.message

    if not msg.content:
        return


async def normalize_message_content(content: str) -> t.Set[str]:
    # Normalize all unicode characters (removes accents, characters that look like other characters,
    # and language characters outside ascii)
    content = unidecode(content)
    # Make it all lowercase
    content = content.lower()
    # Remove all numbers
    content = re.sub(r"\d+", "", content)
    # Remove all punctuation (everything that's not a word)
    content = re.sub(r"[^\w\s]", "", content)
    # Remove any character that's not ASCII
    content = re.sub(r"[^\x00-\x7F]+", "", content)
    # Remove heading and footing whitespaces
    content = content.strip()
    # Split all the words (by newline and whitespaces)
    words_list = content.split()
    # Deduplicate the words and make search O(1)
    words_set = set(words_list)

    return words_set


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
