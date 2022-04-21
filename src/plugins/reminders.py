import re
import datetime

import hikari
import lightbulb
from lightbulb.ext import tasks

from src import utils, main

plugin = utils.Plugin("Meta commands")

regex = re.compile(
    r"((?P<years>\d+?)(Y|y|years|year|A|a|anys|any|año|años))?((?P<months>\d+?)(M|months|month|mes))?((?P<weeks>\d+?)(W|w|weeks|week|S|setmana|setmanes|semanas|semana))?((?P<days>\d+?)(D|d|days|day|dias|dia))?((?P<hours>\d+?)(H|h|hr|hours|hour|hora|horas))?((?P<minutes>\d+?)(m|min|minutes|minuts|minuto|minutos|minut))?((?P<seconds>\d+?)(s|sec|seconds|segons|segons|segundo|segundos))?"
)


@plugin.command()
@lightbulb.option(
    "message",
    "Quin missatge vols que et recordi?",
    required=False,
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.option("time", "Al cap de quant temps t'he de recordar?", required=True)
@lightbulb.command("reminder", "Comandes sobre recordatoris", auto_defer=True)
@lightbulb.implements(
    lightbulb.PrefixCommandGroup,
    lightbulb.SlashCommandGroup,
)
async def reminder(ctx: utils.Context) -> None:
    await create_reminder(ctx)


@reminder.child
@lightbulb.option(
    "message",
    "Quin missatge vols que et recordi?",
    required=False,
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.option("time", "Al cap de quant temps t'he de recordar?", required=True)
@lightbulb.command("create", "Crea un recordatori", auto_defer=True)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def create_reminder(ctx: utils.Context) -> None:
    """
    Reminds the user of a message.
    """
    match = regex.match(ctx.options.time)

    if not match:
        await ctx.respond("No he pogut entendre el temps que has especificat.")
        return

    time = 0

    if match.group("years"):
        time += int(match.group("years")) * 31536000
    if match.group("months"):
        time += int(match.group("months")) * 2592000
    if match.group("weeks"):
        time += int(match.group("weeks")) * 604800
    if match.group("days"):
        time += int(match.group("days")) * 86400
    if match.group("hours"):
        time += int(match.group("hours")) * 3600
    if match.group("minutes"):
        time += int(match.group("minutes")) * 60
    if match.group("seconds"):
        time += int(match.group("seconds"))

    if time < 60:
        await ctx.respond("El temps del recordatori es massa curt.")
        return

    time = datetime.datetime.now() + datetime.timedelta(seconds=time)

    if isinstance(ctx, lightbulb.PrefixContext):
        message_id = ctx.event.message.id
    else:
        message_id = None

    async with ctx.bot.db.execute(
        "INSERT INTO reminder (user_id, message_id, channel_id, guild_id, time, content) VALUES (?, ?, ?, ?, ?, ?) RETURNING id",
        (
            ctx.author.id,
            message_id,
            ctx.channel_id,
            ctx.guild_id,
            time,
            ctx.options.message or None,
        ),
    ) as cursor:
        row = await cursor.fetchone()
        assert row
        reminder_id = row[0]

    await ctx.bot.db.commit()

    await ctx.respond(
        f"Recordatori guardat! El recordatori sera enviat <t:{int(time.timestamp())}:F>!\nID: {reminder_id}"
    )


@reminder.child
@lightbulb.option(
    "reminder_id", "Quin recordatori vols cancel·lar?", int, required=True
)
@lightbulb.command("delete", "Elimina un recordatori.", auto_defer=True)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def delete_reminder(ctx: utils.Context) -> None:
    """
    Deletes a reminder.
    """
    if not ctx.options.reminder_id:
        await ctx.respond("No he pogut entendre l'ID del recordatori.")
        return

    async with ctx.bot.db.execute(
        "DELETE FROM reminder WHERE id = ? AND user_id = ? RETURNING id",
        (ctx.options.reminder_id, ctx.author.id),
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            await ctx.respond("No tens cap recordatori amb aquesta ID.")
            return

    await ctx.bot.db.commit()

    await ctx.respond("Recordatori eliminat!")


@reminder.child
@lightbulb.command(
    "clear",
    "Elimina tots els recordatoris.",
    auto_defer=True,
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def clear_reminders(ctx: utils.Context) -> None:
    """
    Deletes all reminders.
    """
    async with ctx.bot.db.execute(
        "DELETE FROM reminder WHERE user_id = ?", (ctx.author.id,)
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            await ctx.respond("No tens cap recordatori.")
            return

    await ctx.bot.db.commit()

    await ctx.respond("Tots els recordatoris eliminats!")


@reminder.child
@lightbulb.option(
    "reminder_id", "Quin recordatori vols cancel·lar?", int, required=True
)
@lightbulb.command(
    "info",
    "Mostra informació sobre un recordatori.",
    auto_defer=True,
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def reminder_info(ctx: utils.Context) -> None:
    """
    Shows information about a reminder.
    """
    if not ctx.options.reminder_id:
        await ctx.respond("No he pogut entendre l'ID del recordatori.")
        return

    async with ctx.bot.db.execute(
        "SELECT id, time, content FROM reminder WHERE id = ? AND user_id = ?",
        (ctx.options.reminder_id, ctx.author.id),
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            await ctx.respond("No tens cap recordatori amb aquest ID.")
            return

    reminder_id, time, message = row
    if message:
        await ctx.respond(
            f"ID: {reminder_id} - <t:{int(time.timestamp())}:F>\nMissatge: {message}"
        )
    else:
        await ctx.respond(
            f"ID: {reminder_id} - <t:{int(time.timestamp())}:F>\nSense missatge."
        )


@reminder.child
@lightbulb.command(
    "list",
    "Mostra una llista de tots els recordatoris.",
    auto_defer=True,
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def list_reminders(ctx: utils.Context) -> None:
    """
    Lists all reminders.
    """
    async with ctx.bot.db.execute(
        "SELECT id, time, content FROM reminder WHERE user_id = ?", (ctx.author.id,)
    ) as cursor:
        rows = await cursor.fetchall()
        if not rows:
            await ctx.respond("No tens cap recordatori.")
            return

    if not rows:
        await ctx.respond("No tens cap recordatori.")
        return

    reminders = []
    for row in rows:
        time: datetime.datetime
        reminder_id, time, message = row

        if message:
            reminders.append(
                f"ID: {reminder_id} - <t:{int(time.timestamp())}:F>\nMissatge: {message}"
            )
        else:
            reminders.append(
                f"ID: {reminder_id} - <t:{int(time.timestamp())}:F>\nSense missatge."
            )

    await ctx.respond("\n\n".join(reminders))


@tasks.task(s=15, pass_app=True, wait_before_execution=True)
async def reminder_task(bot: main.CiberBot) -> None:
    """
    Task that sends reminders.
    """
    async with bot.db.execute(
        "SELECT id, time, content, user_id, message_id, channel_id, guild_id FROM reminder WHERE time < ?",
        (datetime.datetime.now(),),
    ) as cursor:
        rows = await cursor.fetchall()
        if not rows:
            return

    for row in rows:
        reminder_id, _, message, user_id, message_id, channel_id, guild_id = row

        embed = hikari.Embed(
            title=f"Recordatori {reminder_id}!",
            description=message,
        )

        if guild_id and message_id:
            embed.url = (
                f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
            )

        await bot.rest.create_message(
            channel_id, f"<@{user_id}>", embed=embed, user_mentions=True
        )

        await bot.db.execute("DELETE FROM reminder WHERE id = ?", (reminder_id,))
        await bot.db.commit()


def load(bot: main.CiberBot) -> None:
    reminder_task.start()
    bot.add_plugin(plugin)
