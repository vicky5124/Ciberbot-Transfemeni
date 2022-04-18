import asyncio
import typing as t

import hikari
import lightbulb
import lavasnek_rs

from src import utils, main

plugin = utils.Plugin("Music (basic) commands")
plugin.add_checks(lightbulb.guild_only)


def generate_embed(info: lavasnek_rs.Info, requester: str) -> hikari.Embed:
    embed = hikari.Embed(title=info.title, url=info.uri)
    embed.set_thumbnail(f"https://i.ytimg.com/vi/{info.identifier}/default.jpg")
    embed.set_footer(text=f"Submited by {requester}")
    embed.add_field(name="Uploader", value=info.author, inline=True)

    current = (info.position / 1000).__trunc__()
    length = (info.length / 1000).__trunc__()

    current_minutes = (current % 3600 / 60).__trunc__()
    current_seconds = (current % 3600 % 60).__trunc__()

    minutes = (length % 3600 / 60).__trunc__()
    seconds = (length % 3600 % 60).__trunc__()

    if length >= 3600:
        current_hours = (current / 3600).__trunc__()
        hours = (length / 3600).__trunc__()

        value = "{}:{:02}:{:02} - {}:{:02}:{:02}".format(
            current_hours, current_minutes, current_seconds, hours, minutes, seconds
        )
    else:
        value = "{:02}:{:02} - {:02}:{:02}".format(
            current_minutes, current_seconds, minutes, seconds
        )

    embed.add_field(
        name="Length",
        value=value,
        inline=True,
    )

    return embed


async def _join(ctx: utils.Context) -> t.Optional[hikari.Snowflake]:
    if not ctx.guild_id:
        return None

    if not ctx.options.channel:
        states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
        voice_state = [
            state
            async for state in states.iterator().filter(
                lambda i: i.user_id == ctx.author.id
            )
        ]

        if not voice_state:
            await ctx.respond("Connectet a un canal de veu primer.")
            return None

        channel_id = voice_state[0].channel_id
    else:
        channel_id = ctx.options.channel.id

    await plugin.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    connection_info = await ctx.bot.lavalink.wait_for_full_connection_info_insert(
        ctx.guild_id
    )

    await ctx.bot.lavalink.destroy(ctx.guild_id)
    await ctx.bot.lavalink.create_session(connection_info)

    return channel_id


@plugin.command()
@lightbulb.option(
    "channel",
    "El canal de veu on entrar.",
    hikari.GuildVoiceChannel,
    required=False,
    channel_types=[hikari.ChannelType.GUILD_VOICE],
)
@lightbulb.command(
    "join", "Entra en el canal de veu on estàs actualment, o el especificat."
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def join(ctx: utils.Context) -> None:
    """Joins the voice channel you are in."""
    channel_id = await _join(ctx)

    if channel_id:
        await ctx.respond(f"M'he unit correctament al canal <#{channel_id}>")


@plugin.command()
@lightbulb.command("leave", "Surt del canal de veu actual, eliminant la cua actual.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def leave(ctx: utils.Context) -> None:
    """Leaves the voice channel the bot is in, clearing the queue."""
    assert ctx.guild_id

    await ctx.bot.lavalink.destroy(ctx.guild_id)

    if ctx.guild_id is not None:
        await ctx.bot.update_voice_state(ctx.guild_id, None)
        await ctx.bot.lavalink.wait_for_connection_info_remove(ctx.guild_id)

    # Destroy nor leave remove the node nor the queue loop, you should do this manually.
    await ctx.bot.lavalink.remove_guild_node(ctx.guild_id)
    await ctx.bot.lavalink.remove_guild_from_loops(ctx.guild_id)

    await ctx.respond("He sortit del canal de veu correctament.")


async def play_base(ctx: utils.Context) -> t.Optional[str]:
    if not ctx.guild_id:
        return None

    query: str = ctx.options.query

    if not query:
        await ctx.respond("Especifica una busqueda o un URL.")
        return None

    con = ctx.bot.lavalink.get_guild_gateway_connection_info(ctx.guild_id)

    if not con:
        await _join(ctx)

    return query


@plugin.command()
@lightbulb.option(
    "query",
    "El terme de busqueda o el URL que afegir.",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.command(
    "play", "Busca la query en YouTube, o afegeix el URL directament a la cua."
)
@lightbulb.implements(
    lightbulb.PrefixCommandGroup,
    lightbulb.SlashCommandGroup,
)
async def play(ctx: utils.Context) -> None:
    """Searches the query on youtube, or adds the URL to the queue."""
    assert ctx.guild_id

    query = await play_base(ctx)

    if not query:
        return

    query_information = await ctx.bot.lavalink.auto_search_tracks(query)

    if not query_information.tracks:  # tracks is empty
        await ctx.respond("No he trobat cap resultat.")
        return

    try:
        await ctx.bot.lavalink.play(
            ctx.guild_id, query_information.tracks[0]
        ).requester(ctx.author.id).queue()
    except lavasnek_rs.NoSessionPresent:
        await ctx.respond(f"Utilitza `/join` primer.")
        return

    await ctx.respond(
        f"Afegit a la cua:",
        embed=generate_embed(query_information.tracks[0].info, ctx.author.username),
    )


@play.child
@lightbulb.option(
    "query",
    "URL amb la llista de reproduccio.",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.command(
    "single", "Busca la query en YouTube, o afegeix el URL directament a la cua."
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def play_single(ctx: utils.Context) -> None:
    """Callback to play"""
    await play(ctx)


@play.child
@lightbulb.option(
    "query",
    "URL amb la llista de reproduccio.",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.command("list", "Afegeix tot el contingut de la URL directament a la cua.")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def play_list(ctx: utils.Context) -> None:
    """Adds all the URL results to the queue."""
    assert ctx.guild_id

    query = await play_base(ctx)

    if not query:
        return

    query_information = await ctx.bot.lavalink.get_tracks(query)

    if not query_information.tracks:  # tracks is empty
        await ctx.respond("No he trobat cap resultat.")
        return

    try:
        for track in query_information.tracks:
            await ctx.bot.lavalink.play(ctx.guild_id, track).requester(
                ctx.author.id
            ).queue()
    except lavasnek_rs.NoSessionPresent:
        await ctx.respond(f"Utilitza `/join` primer.")
        return

    await ctx.respond(f"Playlist Afegida a la cua: <{query}>")


@plugin.command()
@lightbulb.command("skip", "Salta la reproduccio.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def skip(ctx: utils.Context) -> None:
    """Skips the current track."""
    assert ctx.guild_id

    track = await ctx.bot.lavalink.skip(ctx.guild_id)

    if not track:
        await ctx.respond("No hi ha cap cançó a la cua.")

        return

    node = await plugin.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or (not node.queue and not node.now_playing):
        await plugin.bot.lavalink.stop(ctx.guild_id)

    requester = ctx.bot.cache.get_user(track.requester)

    if not requester:
        username = "Unknown"
    else:
        username = requester.username

    await ctx.respond(f"Saltat:", embed=generate_embed(track.track.info, username))


@plugin.command()
@lightbulb.command("queue", "Mostra la cua.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def queue(ctx: utils.Context) -> None:
    """Shows the current queue."""
    assert ctx.guild_id

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        await ctx.respond("La cua està buida.")
        return

    tracks = [
        f"\u001b[1m\u001b[35m{idx + 1}: \u001b[0m\u001b[34m{track.track.info.title}"
        for idx, track in enumerate(node.queue)
    ]

    per_page = 10

    if len(tracks) <= per_page:
        tracks_str = "\n".join(tracks)
        await ctx.respond(
            f"Cua amb {len(node.queue)} elements: ```ansi\n{tracks_str}\n```"
        )
    else:
        start: int = 0
        end: int = per_page

        components = ctx.bot.rest.build_action_row()

        button_start = components.add_button(1, "start")
        button_prev = components.add_button(1, "prev")
        button_next = components.add_button(1, "next")
        button_end = components.add_button(1, "end")

        button_start.set_emoji("⏮️")
        button_prev.set_emoji("⬅️")
        button_next.set_emoji("➡️")
        button_end.set_emoji("⏭️")

        button_start.add_to_container()
        button_prev.add_to_container()
        button_next.add_to_container()
        button_end.add_to_container()

        def predicate(event: hikari.InteractionCreateEvent) -> bool:
            return event.interaction.type == 3 and isinstance(
                event.interaction, hikari.ComponentInteraction
            )

        tracks_str = "\n".join(tracks[start:end])
        msg = await ctx.respond(
            f"Cua amb {len(node.queue)} elements: ```ansi\n{tracks_str}\n```",
            component=components,
        )

        while True:
            try:
                event = await ctx.bot.wait_for(
                    hikari.InteractionCreateEvent, timeout=30, predicate=predicate
                )
            except asyncio.TimeoutError:
                await msg.edit(component=None)
                return

            assert isinstance(event.interaction, hikari.ComponentInteraction)

            if event.interaction.custom_id == button_prev.custom_id:
                start -= per_page
                end -= per_page

                if start < 0:
                    start = 0
                    end = per_page
            elif event.interaction.custom_id == button_next.custom_id:
                start += per_page
                end += per_page

                if end > len(tracks):
                    end = len(tracks)
                    start = end - per_page
            elif event.interaction.custom_id == button_start.custom_id:
                start = 0
                end = per_page
            elif event.interaction.custom_id == button_end.custom_id:
                start = len(tracks) - per_page
                end = len(tracks)

            tracks_str = "\n".join(tracks[start:end])
            await event.interaction.create_initial_response(
                7,
                f"Cua amb {len(node.queue)} elements: ```ansi\n{tracks_str}\n```",
                component=components,
            )


@plugin.command()
@lightbulb.command(
    "now_playing", "Mostra la canço que esta reproduint.", aliases=["np"]
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def now_playing(ctx: utils.Context) -> None:
    """Shows the current track."""
    assert ctx.guild_id

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        await ctx.respond("No hi ha cap cançó a la cua.")
        return

    track = node.now_playing

    requester = ctx.bot.cache.get_user(track.requester)

    if not requester:
        username = "Unknown"
    else:
        username = requester.username

    await ctx.respond(f"Reproduint:", embed=generate_embed(track.track.info, username))


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)