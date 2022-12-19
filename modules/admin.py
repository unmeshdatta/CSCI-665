import hikari
import lightbulb
import time


from db.models import User, Raffle, Guild, RaffleEntry
from utils.tstr import convert
from utils.embedfielditerator import iterator
from utils.responses import pos, _pos, err
from utils.module import Module

p = Module('Admin')


p.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))


@p.command()
@lightbulb.option("duration", "The duration of the raffle.",
                  required=False, default="1d")
@lightbulb.option("entryfee", "The required entry fee.", type=int)
@lightbulb.option("prize", "The prize for this raffle.")
@lightbulb.command("create", "Create a raffle.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def create(ctx: lightbulb.Context):
    guild: Guild = Guild.get_or_create(gid=ctx.guild_id)[0]
    duration = convert(ctx.options.duration)
    if not duration:
        raise lightbulb.errors.ConverterFailure(opt="duration", raw=ctx.options.duration)
    end = time.time() + duration
    raffle: Raffle = Raffle.create(guild=guild, prize=ctx.options.prize,
            end=end, fee=ctx.options.entryfee, channel_id=guild.raffle_channel)
    embe = _pos(f"Raffle `{raffle.id}`", description=f"Prize: `{raffle.prize}`\nEnds: <t:{int(raffle.end)}:R>\nFee: `{raffle.fee}`\nJoin using /Join")
    if p._config.raffle_ongoing:
        embe.set_image(p._config.raffle_ongoing)
    mes = await p.bot.rest.create_message(guild.raffle_channel, embed=embe)
    raffle.message_id = mes.id
    raffle.save()
    await pos(ctx, "Success!", f"Succesfully created Raffle `{raffle.id}`")


@p.command()
@lightbulb.option("amount", "The amount of tokens you want to give.", type=int)
@lightbulb.option("user", "The user you want to give the tokens to.", type=hikari.Member)
@lightbulb.command("give", "Give tokens to a user.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def give(ctx: lightbulb.Context):
    guild: Guild = Guild.get_or_create(gid=ctx.guild_id)[0]
    user: hikari.Member = ctx.options.user
    duser: User = User.get_or_create(userid=user.id, guild=guild)[0]
    duser.balance += ctx.options.amount
    duser.save()
    return await pos(ctx, "Success!", f"Succesfully given `{ctx.options.amount}` to {user.mention}.", delete_after=5)


@p.command()
@lightbulb.option("id", "The id of the raffle you want to end.", type=int)
@lightbulb.command("end", "End a raffle sooner.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def end(ctx: lightbulb.Context):
    guild: Guild = Guild.get_or_create(gid=ctx.guild_id)[0]
    raffle: Raffle | None = Raffle.get_or_none(id=ctx.options.id, guild=guild)
    if not raffle:
        return await err(ctx, "Error", "Raffle with the given id doesn't exist!", delete_after=5)
    elif raffle.finished:
        return await err(ctx, "Error", f"Raffle `{raffle.id}` has already finished!", delete_after=5)
    else:
        raffle.end = time.time()
        raffle.save()
        return await pos(ctx, "Success!", "Succesfully set the auction's end time to now.", delete_after=5)

@p.command()
@lightbulb.option("id", "The id of the raffle.", type=int)
@lightbulb.command("list", "List all Raffle participants.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def end(ctx: lightbulb.Context):
    guild: Guild = Guild.get_or_create(gid=ctx.guild_id)[0]
    raffle: Raffle | None = Raffle.get_or_none(id=ctx.options.id, guild=guild)
    if not raffle:
        return await err(ctx, "Error", "Raffle with the given id doesn't exist!", delete_after=5)
    else:
        values = [(f"Entered <t:{entry.time}:R>:", f'<@{entry.user.userid}>') for entry in raffle.entries]
        await iterator(ctx, f"Users who entered Raffle `{raffle.id}`", values)


def load(bot : lightbulb.BotApp) -> None:
	bot.add_plugin(p)

def unload(bot : lightbulb.BotApp) -> None:
	bot.remove_plugin(p)
