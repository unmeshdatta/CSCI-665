import lightbulb
import hikari
import time
from peewee import fn
from lightbulb.ext import tasks

from db.models import Guild, User, Raffle, RaffleEntry
from utils.module import Module
from utils.responses import pos, _pos, err
from utils.embedfielditerator import iterator


p = Module('Raffles')

async def set_guild_raffle_channel(dguild: Guild, guild: hikari.Guild):
    found = False
    for channel in await p.bot.rest.fetch_guild_channels(guild):
        if channel.name == p._config.raffle_channel_name:
            found = True
            dguild.raffle_channel = channel.id
    if not found:
        cha = await p.bot.rest.create_guild_text_channel(guild, name=p._config.raffle_channel_name)
        dguild.raffle_channel = cha.id
    dguild.save()
    return dguild.raffle_channel


@p.listener(hikari.ShardReadyEvent)
async def on_ready(event: hikari.ShardReadyEvent):
    async for guild in p.bot.rest.fetch_my_guilds():
        dguild: Guild = Guild.get_or_create(gid=guild.id)[0]
        if dguild.raffle_channel:
            try:
                cha = await p.bot.rest.fetch_channel(dguild.raffle_channel)
            except:
                await set_guild_raffle_channel(dguild, guild)
        else:
            await set_guild_raffle_channel(dguild, guild)
    dguild.save()


@p.listener(hikari.GuildJoinEvent)
async def on_guild_join(event: hikari.GuildJoinEvent):
    guild = event.guild
    dguild: Guild = Guild.get_or_create(gid=guild.id)[0]
    if dguild.raffle_channel:
        try:
            cha = await p.bot.rest.fetch_channel(dguild.raffle_channel)
        except:
            await set_guild_raffle_channel(dguild, guild)
    else:
        await set_guild_raffle_channel(dguild, guild)


@p.command()
@lightbulb.option("id", "The id of the raffle you want to join.", type=int)
@lightbulb.command("join", "Join a raffle..")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def join(ctx: lightbulb.Context):
    guild: Guild = Guild.get_or_create(gid=ctx.guild_id)[0]
    raffle: Raffle | None = Raffle.get_or_none(id=ctx.options.id, guild=guild)
    if not raffle:
        return await err(ctx, "Error", "Raffle with the given id doesn't exist!", delete_after=5)
    elif raffle.finished:
        return await err(ctx, "Error", f"Raffle `{raffle.id}` has already finished!", delete_after=5)
    else:
        user: User = User.get_or_create(userid=ctx.author.id, guild=guild)[0]
        if user.balance<raffle.fee:
            return await err(ctx, "Error", "Your balance is too low!", delete_after=5)
        user.balance -= raffle.fee
        user.save()
        rae = RaffleEntry.get_or_none(user=user, raffle=raffle)
        if rae:
            return await err(ctx, "Error", "You already joined this raffle!", delete_after=5)
        RaffleEntry.create(user=user, raffle=raffle)
        return await pos(ctx, "Sucess!", f"You succesfully joined Raffle `{raffle.id}`", delete_after=5)


@tasks.task(s=10)
async def check_for_finished(*args):
    raffles: list[Raffle] = (Raffle.select().where((Raffle.finished==False) & (Raffle.end<time.time())).execute())
    for raffle in raffles:
            raffle.finished = True
            raffle.save()
            winner = list((RaffleEntry.select().where(RaffleEntry.raffle==raffle).order_by(fn.Random()).limit(1)).execute())
            if winner:
                raffle.winner = winner[0].user
                raffle.save()
                embe = _pos(f"Raffle `{raffle.id}` has finished!", f"<@{raffle.winner.userid}> has won `{raffle.prize}`!")
                if p._config.raffle_ended:
                    embe.set_image(p._config.raffle_ended)
            else:
                embe = _pos(f"Raffle `{raffle.id}` has finished without winners!")
                if p._config.raffle_ended_no_winners:
                    embe.set_image(p._config.raffle_ended_no_winners)
            #await p.bot.rest.edit_message(raffle.channel_id, raffle.message_id, embed=embe)
            try:await p.bot.rest.delete_message(raffle.channel_id, raffle.message_id)
            except:pass
            try:await p.bot.rest.create_message(raffle.guild.raffle_channel, embed=embe)
            except:
                chaid = await set_guild_raffle_channel(raffle.guild, raffle.guild.gid)
                await p.bot.rest.create_message(chaid, embed=embe)



def load(bot : lightbulb.BotApp) -> None:
    check_for_finished.start()
    bot.add_plugin(p)

def unload(bot : lightbulb.BotApp) -> None:
	bot.remove_plugin(p)
