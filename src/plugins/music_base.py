import logging

import hikari
import lightbulb
import lavasnek_rs

from src import utils, main

plugin = utils.Plugin("Music (base) events")
plugin.add_checks(lightbulb.guild_only)


class EventHandler:
    """Events from the Lavalink server"""

    async def track_exception(
        self, lavalink: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackException
    ) -> None:
        logging.warning("Track exception event happened on guild: %d", event.guild_id)

        # If a track was unable to be played, skip it
        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not node:
            return

        if skip and not node.queue and not node.now_playing:
            await lavalink.stop(event.guild_id)


@plugin.listener(hikari.ShardReadyEvent, bind=True)
async def start_lavalink(plug: utils.Plugin, event: hikari.ShardReadyEvent) -> None:
    """Event that triggers when the hikari gateway is ready."""

    builder = (
        lavasnek_rs.LavalinkBuilder(event.my_user.id, "")
        .set_host(plug.bot.config.lavalink.host)
        .set_password(plug.bot.config.lavalink.password)
        .set_port(plug.bot.config.lavalink.port)
        .set_start_gateway(False)
    )

    lavalink = await builder.build(EventHandler())

    plug.bot.lavalink = lavalink


@plugin.listener(hikari.VoiceStateUpdateEvent, bind=True)
async def voice_state_update(
    plug: utils.Plugin, event: hikari.VoiceStateUpdateEvent
) -> None:
    plug.bot.lavalink.raw_handle_event_voice_state_update(
        event.state.guild_id,
        event.state.user_id,
        event.state.session_id,
        event.state.channel_id,
    )


@plugin.listener(hikari.VoiceServerUpdateEvent, bind=True)
async def voice_server_update(
    plug: utils.Plugin, event: hikari.VoiceServerUpdateEvent
) -> None:
    if not event.endpoint:
        return

    await plug.bot.lavalink.raw_handle_event_voice_server_update(
        event.guild_id, event.endpoint, event.token
    )


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
