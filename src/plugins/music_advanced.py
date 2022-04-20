import random

import lightbulb

from src import utils, main

plugin = utils.Plugin("Music (advanced) commands")
plugin.add_checks(lightbulb.guild_only)


@plugin.command()
@lightbulb.command("pause", "Pausa la reproducció")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pause(ctx: utils.Context) -> None:
    """Pauses the current track."""
    assert ctx.guild_id

    await ctx.bot.lavalink.pause(ctx.guild_id)

    await ctx.respond("Pausat.")


@plugin.command()
@lightbulb.command("resume", "Reprendre la reproducció")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def resume(ctx: utils.Context) -> None:
    """Resumes the current track."""
    assert ctx.guild_id

    await ctx.bot.lavalink.resume(ctx.guild_id)

    await ctx.respond("Reproducció represa.")


@plugin.command()
@lightbulb.command("stop", "Atura la reproducció")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def stop(ctx: utils.Context) -> None:
    """Stops the current track."""
    assert ctx.guild_id

    await ctx.bot.lavalink.stop(ctx.guild_id)

    await ctx.respond("Aturat.")


@plugin.command()
@lightbulb.option("index", "L'índex de la cançó a eliminar", type=int)
@lightbulb.command("remove", "Elimina una cançó de la cua")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def remove(ctx: utils.Context) -> None:
    """Removes a track from the queue."""
    assert ctx.guild_id

    index = ctx.options.index

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        await ctx.respond("No n'hi ha cap cançó a la cua.")
        return

    try:
        queue = node.queue
        track = queue.pop(index - 1)
        node.queue = queue

        await ctx.bot.lavalink.set_guild_node(ctx.guild_id, node)
    except IndexError:
        await ctx.respond("L'índex no és vàlid.")
        return

    await ctx.respond(f"Eliminat: {track.track.info.title}")


@plugin.command()
@lightbulb.command("clear", "Elimina tota la cua")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def clear(ctx: utils.Context) -> None:
    """Clears the queue."""
    assert ctx.guild_id

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        await ctx.respond("La cua ja es buida.")
        return

    queue = node.queue[1:]
    np = node.queue[0]
    queue.clear()
    queue.insert(0, np)
    node.queue = queue

    await ctx.bot.lavalink.set_guild_node(ctx.guild_id, node)

    await ctx.respond("Cua buidada.")


@plugin.command()
@lightbulb.option("position", "El segon en la cançó on saltar", type=int)
@lightbulb.command("seek", "Salta a una posició determinada")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def seek(ctx: utils.Context) -> None:
    """Seek to a position in the track."""
    assert ctx.guild_id

    position = ctx.options.position

    await ctx.bot.lavalink.seek_secs(ctx.guild_id, position)

    await ctx.respond(f"Saltat a `{int(position / 60):02}:{int(position % 60):02}`.")


@plugin.command()
@lightbulb.command("shuffle", "Barreja la cua")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def shuffle(ctx: utils.Context) -> None:
    """Shuffles the queue."""
    assert ctx.guild_id

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        await ctx.respond("No n'hi ha cap cançó a la cua.")
        return

    queue = node.queue[1:]
    np = node.queue[0]
    queue = random.sample(queue, k=len(queue))
    queue.insert(0, np)
    node.queue = queue

    await ctx.bot.lavalink.set_guild_node(ctx.guild_id, node)

    await ctx.respond("Cua barrejada.")


@plugin.command()
@lightbulb.option("index1", "El primer índex a la cua")
@lightbulb.option("index2", "El segon índex a la cua")
@lightbulb.command("swap", "Intercanvia la posició de dos elements de la cua")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def swap(ctx: utils.Context, index1: int, index2: int) -> None:
    """Swaps the position of 2 items in the queue."""
    assert ctx.guild_id

    index1 = ctx.options.index1
    index2 = ctx.options.index2

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        await ctx.respond("No n'hi ha cap cançó a la cua.")
        return

    if index1 < 0 or index1 >= len(node.queue):
        await ctx.respond("Index 1 no és vàlid.")
        return

    if index2 < 0 or index2 >= len(node.queue):
        await ctx.respond("Index 2 no és vàlid.")
        return

    if index1 == index2:
        await ctx.respond("Els dos index són el mateix.")
        return

    track1 = node.queue[index1]
    track2 = node.queue[index2]

    queue = node.queue

    queue[index1] = track2
    queue[index2] = track1

    node.queue = queue

    await ctx.bot.lavalink.set_guild_node(ctx.guild_id, node)

    await ctx.respond("Cançons intercanvades.")


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
