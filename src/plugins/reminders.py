import re
import datetime

import hikari
import lightbulb
import shortuuid
from lightbulb.ext import tasks

from src import utils, main

plugin = utils.Plugin("Meta commands")

regex = re.compile(
    r"((?P<years>\d+?)(Y|y|years|year|A|a|anys|any|año|años))?((?P<months>\d+?)(M|months|month|mes))?((?P<weeks>\d+?)(W|w|weeks|week|S|setmana|setmanes|semanas|semana))?((?P<days>\d+?)(D|d|days|day|dias|dia))?((?P<hours>\d+?)(H|h|hr|hours|hour|hora|horas))?((?P<minutes>\d+?)(m|min|minutes|minuts|minuto|minutos|minut))?((?P<seconds>\d+?)(s|sec|seg|seconds|segons|segon|segundo|segundos))?"
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
        await ctx.respond("El temps del recordatori és massa curt.")
        return

    time = datetime.datetime.now() + datetime.timedelta(seconds=time)

    if isinstance(ctx, lightbulb.PrefixContext):
        message_id = ctx.event.message.id
    else:
        message_id = None

    shortuuid.set_alphabet("23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
    reminder_id = shortuuid.uuid()[:8]

    await ctx.bot.db.execute_asyncio(
        "INSERT INTO reminder (id, user_id, message_id, channel_id, guild_id, datetime, content) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            reminder_id,
            ctx.author.id,
            message_id,
            ctx.channel_id,
            ctx.guild_id,
            time,
            ctx.options.message or None,
        ),
    )

    await ctx.respond(
        f"Recordatori guardat! El recordatori serà enviat <t:{int(time.timestamp())}:F>!\nID: {reminder_id}"
    )


@reminder.child
@lightbulb.option(
    "reminder_id", "Quin recordatori vols cancel·lar?", str, required=True
)
@lightbulb.command("delete", "Elimina un recordatori.", auto_defer=True)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def delete_reminder(ctx: utils.Context) -> None:
    """
    Deletes a reminder.
    """
    if not ctx.options.reminder_id:
        await ctx.respond("No he pogut entendre la ID del recordatori.")
        return

    if len(ctx.options.reminder_id) != 8:
        await ctx.respond("La ID és invàlida.")
        return

    row = await ctx.bot.db.execute_asyncio(
        "SELECT id, user_id, datetime FROM reminder WHERE id = %s AND user_id = %s",
        (ctx.options.reminder_id.upper(), ctx.author.id),
    )

    reminder_pks = row.one()

    if not reminder_pks:
        await ctx.respond("No tens cap recordatori amb aquesta ID.")
        return

    await ctx.bot.db.execute_asyncio(
        "DELETE FROM reminder WHERE id = %s AND user_id = %s AND datetime = %s",
        (reminder_pks.id, reminder_pks.user_id, reminder_pks.datetime),
    )

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
    rows = await ctx.bot.db.execute_asyncio(
        "SELECT id, datetime FROM reminder WHERE user_id = %s", (ctx.author.id,)
    )

    if not rows:
        await ctx.respond("No tens cap recordatori.")
        return

    for i in rows:
        await ctx.bot.db.execute_asyncio(
            "DELETE FROM reminder WHERE user_id = %s AND id = %s AND datetime = %s",
            (ctx.author.id, i.id, i.datetime),
        )

    await ctx.respond("Tots els recordatoris han sigut eliminats!")


@reminder.child
@lightbulb.option(
    "reminder_id", "Quin recordatori vols cancel·lar?", str, required=True
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
        await ctx.respond("No he pogut entendre la ID del recordatori.")
        return

    if len(ctx.options.reminder_id) != 8:
        await ctx.respond("La ID és invàlida.")
        return

    row = await ctx.bot.db.execute_asyncio(
        "SELECT id, datetime, content FROM reminder WHERE user_id = %s AND id = %s",
        (ctx.author.id, ctx.options.reminder_id.upper()),
    )

    if not row:
        await ctx.respond("No tens cap recordatori amb aquest ID.")
        return

    row = row.one()

    if row.content:
        await ctx.respond(
            f"ID: {row.id} - <t:{int(row.datetime.timestamp())}:F>\nMissatge: {row.content}"
        )
    else:
        await ctx.respond(
            f"ID: {row.id} - <t:{int(row.datetime.timestamp())}:F>\nSense missatge."
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
    rows = await ctx.bot.db.execute_asyncio(
        "SELECT id, datetime, content FROM reminder WHERE user_id = %s",
        (ctx.author.id,),
    )

    if not rows:
        await ctx.respond("No tens cap recordatori.")
        return

    reminders = []

    for row in rows:
        if row.content:
            reminders.append(
                f"ID: {row.id} - <t:{int(row.datetime.timestamp())}:F>\nMissatge: {row.content}"
            )
        else:
            reminders.append(
                f"ID: {row.id} - <t:{int(row.datetime.timestamp())}:F>\nSense missatge."
            )

    await ctx.respond("\n\n".join(reminders))


@tasks.task(s=15, pass_app=True, wait_before_execution=True)
async def reminder_task(bot: main.CiberBot) -> None:
    """
    Task that sends reminders.
    """

    # logging.info("TASK RUNNING")

    rows = await bot.db.execute_asyncio(
        "SELECT id, datetime, content, user_id, message_id, channel_id, guild_id FROM reminder WHERE datetime < %s ALLOW FILTERING",
        (datetime.datetime.now(),),
    )

    if not rows:
        return

    for row in rows:
        embed = hikari.Embed(
            title=f"Recordatori {row.id}!",
            description=row.content,
        )

        if row.guild_id and row.message_id:
            embed.url = f"https://discord.com/channels/{row.guild_id}/{row.channel_id}/{row.message_id}"

        await bot.rest.create_message(
            row.channel_id, f"<@{row.user_id}>", embed=embed, user_mentions=True
        )

        await bot.db.execute_asyncio(
            "DELETE FROM reminder WHERE id = %s AND user_id = %s AND datetime = %s",
            (row.id, row.user_id, row.datetime),
        )


def load(bot: main.CiberBot) -> None:
    reminder_task.start()
    bot.add_plugin(plugin)
