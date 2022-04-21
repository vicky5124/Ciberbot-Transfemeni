import logging
import typing as t

import hikari

from src import utils, main

plugin = utils.Plugin("Reaction roles", include_datastore=True)


@plugin.listener(hikari.StartingEvent, bind=True)
async def load_roles_and_emojis(plug: utils.Plugin, _: hikari.StartingEvent) -> None:
    reaction_roles = plug.bot.config.reaction_roles

    rr: t.Dict[int, t.Dict[str, int]] = {}

    for (key, value) in reaction_roles.items():
        logging.info(f"Loading reaction role '{key}'")
        rr[value.message_id] = dict(zip(value.emoji_names, value.role_ids))

    plug.d.reaction_roles = rr


@plugin.listener(hikari.GuildReactionAddEvent, bind=True)
async def reaction_add_event(
    plug: utils.Plugin, event: hikari.GuildReactionAddEvent
) -> None:
    for (message_id, rr) in plug.d.reaction_roles.items():
        if event.message_id == message_id:
            emoji_name = str(event.emoji_name)

            role_id = rr.get(emoji_name)

            if role_id:
                await plug.bot.rest.add_role_to_member(
                    event.guild_id, event.user_id, role_id
                )


@plugin.listener(hikari.GuildReactionDeleteEvent, bind=True)
async def reaction_remove_event(
    plug: utils.Plugin, event: hikari.GuildReactionDeleteEvent
) -> None:
    for (message_id, rr) in plug.d.reaction_roles.items():
        if event.message_id == message_id:
            emoji_name = str(event.emoji_name)

            role_id = rr.get(emoji_name)

            if role_id:
                await plug.bot.rest.remove_role_from_member(
                    event.guild_id, event.user_id, role_id
                )


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
