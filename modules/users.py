import time
import hikari
import lightbulb

from db.models import Guild, User
from utils.module import Module
from utils.responses import pos, err

p = Module('Users')

@p.command()
@lightbulb.command("daily","Get the daily bonus.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def daily(ctx: lightbulb.Context):
    guild: Guild = Guild.get_or_create(gid=ctx.guild_id)[0]
    user: User = User.get_or_create(userid=ctx.author.id, guild=guild)[0]
    if user.cooldown< time.time():
        user.balance+= p._config.daily_bonus_amount
        user.cooldown = time.time() + p._config.daily_bonus_delay
        user.save()
        return await pos(ctx, "Success!", f"You succesfully claimed the daily `{p._config.daily_bonus_amount}` tokens!\nYour balance is now `{user.balance}` tokens!", delete_after=5)
    else:
        return await err(ctx, "You're still on cooldown!", f"Your cooldown ends <t:{int(user.cooldown)}:R>", delete_after=5)


@p.command()
@lightbulb.option("user", "The user whose balance you want to check. Leave empty to check your balance.", type=hikari.Member, default=None)
@lightbulb.command("balance", "Check your balance.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def balance(ctx: lightbulb.Context):
    guild: Guild = Guild.get_or_create(gid=ctx.guild_id)[0]
    ouser: hikari.Member = ctx.options.user
    if ouser:
        referer, id = f"{ouser.username}#{ouser.discriminator}'s", ouser.id  
    else:
        referer, id = "Your", ctx.author.id
    user: User = User.get_or_create(userid=id, guild=guild)[0]
    return await pos(ctx, f"{referer} balance is `{user.balance}` tokens", "To earn more tokens use the /daily command", delete_after=5)


def load(bot : lightbulb.BotApp) -> None:
	bot.add_plugin(p)

def unload(bot : lightbulb.BotApp) -> None:
	bot.remove_plugin(p)
