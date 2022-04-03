import hikari

from src import utils, main

plugin = utils.Plugin("Reaction roles", include_datastore=True)


@plugin.listener(hikari.StartingEvent, bind=True)
async def load_roles_and_emojis(plug: utils.Plugin, _: hikari.StartingEvent) -> None:
    conf = plug.bot.config.reaction_roles
    plug.d.roles_emojis = dict(
        zip(conf.color_roles.emoji_names, conf.color_roles.role_ids)
    )


@plugin.listener(hikari.GuildReactionAddEvent, bind=True)
async def reaction_add_event(
    plug: utils.Plugin, event: hikari.GuildReactionAddEvent
) -> None:
    conf = plug.bot.config.reaction_roles

    if event.message_id == conf.color_roles.message_id:
        emoji_name = str(event.emoji_name)

        role_id = plug.d.roles_emojis.get(emoji_name)

        if role_id:
            await plug.bot.rest.add_role_to_member(
                event.guild_id, event.user_id, role_id
            )


@plugin.listener(hikari.GuildReactionDeleteEvent, bind=True)
async def reaction_remove_event(
    plug: utils.Plugin, event: hikari.GuildReactionDeleteEvent
) -> None:
    conf = plug.bot.config.reaction_roles

    if event.message_id == conf.color_roles.message_id:
        emoji_name = str(event.emoji_name)

        role_id = plug.d.roles_emojis.get(emoji_name)

        if role_id:
            await plug.bot.rest.remove_role_from_member(
                event.guild_id, event.user_id, role_id
            )


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
