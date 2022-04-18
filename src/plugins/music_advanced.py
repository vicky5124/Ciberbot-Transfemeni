import random

import lightbulb

from src import utils, main

plugin = utils.Plugin("Music (advanced) commands")
plugin.add_checks(lightbulb.guild_only)


@plugin.command()
@lightbulb.command("pause", "Pausa la reproduccio.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pause(ctx: utils.Context) -> None:
    """Pauses the current track."""
    assert ctx.guild_id

    await ctx.bot.lavalink.pause(ctx.guild_id)

    await ctx.respond("Pausat.")


@plugin.command()
@lightbulb.command("resume", "Reprdeix la reproduccio.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def resume(ctx: utils.Context) -> None:
    """Resumes the current track."""
    assert ctx.guild_id

    await ctx.bot.lavalink.resume(ctx.guild_id)

    await ctx.respond("Reproduccio represa.")


@plugin.command()
@lightbulb.command("stop", "Atura la reproduccio.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def stop(ctx: utils.Context) -> None:
    """Stops the current track."""
    assert ctx.guild_id

    await ctx.bot.lavalink.stop(ctx.guild_id)

    await ctx.respond("Aturat.")


@plugin.command()
@lightbulb.option("index", "L'index de la canço a eliminar.", type=int)
@lightbulb.command("remove", "Elimina una canço de la cua.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def remove(ctx: utils.Context) -> None:
    """Removes a track from the queue."""
    assert ctx.guild_id

    index = ctx.options.index

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        await ctx.respond("La cua està buida.")
        return

    try:
        queue = node.queue
        track = queue.pop(index - 1)
        node.queue = queue

        await ctx.bot.lavalink.set_guild_node(ctx.guild_id, node)
    except IndexError:
        await ctx.respond("L'index no es valid.")
        return

    await ctx.respond(f"Eliminat: {track.track.info.title}")


@plugin.command()
@lightbulb.command("clear", "Elimina tota la cua.")
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

    await ctx.respond("Cua buida.")


@plugin.command()
@lightbulb.option("position", "El segon la canço on saltar.", type=int)
@lightbulb.command("seek", "Salta a una posicio determinada.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def seek(ctx: utils.Context) -> None:
    """Seek to a position in the track."""
    assert ctx.guild_id

    position = ctx.options.position

    await ctx.bot.lavalink.seek_secs(ctx.guild_id, position)

    await ctx.respond(f"Saltat a `{int(position / 60):02}:{int(position % 60):02}`.")


@plugin.command()
@lightbulb.command("shuffle", "Barreja la cua.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def shuffle(ctx: utils.Context) -> None:
    """Shuffles the queue."""
    assert ctx.guild_id

    node = await ctx.bot.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        await ctx.respond("La cua està buida.")
        return

    queue = node.queue[1:]
    np = node.queue[0]
    queue = random.sample(queue, k=len(queue))
    queue.insert(0, np)
    node.queue = queue

    await ctx.bot.lavalink.set_guild_node(ctx.guild_id, node)

    await ctx.respond("Cua barrejada.")


def load(bot: main.CiberBot) -> None:
    bot.add_plugin(plugin)
