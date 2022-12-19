#/usr/bin/python
import lightbulb, hikari
from lightbulb.ext import tasks

from db import init_db
from utils.botapp import BotApp
from utils.config import load_config

from sys import argv
if "--debug" in argv:
	config = load_config('config copy.json')

	db = init_db(f'{config.db_root}/service.debug.db')
	debug = True
else:
	config = load_config('config.json')

	db = init_db(f'{config.db_root}/service.db')
	debug = False


bot = BotApp(
    config=config,
	debug = debug,
	token = config.discord_token,
	prefix = lightbulb.when_mentioned_or(config.prefix),
	intents = hikari.Intents.ALL,
	delete_unbound_commands = True,
	case_insensitive_prefix_commands = True,
	owner_ids = [config.owner_id],
	default_enabled_guilds = config.debug_guilds,
)

tasks.load(bot)

@bot.listen(hikari.StartingEvent)
async def starting_listener(event : hikari.StartingEvent) -> None:
	bot.load_extensions_from("./modules/", must_exist=True)


@bot.listen(hikari.StartedEvent)
async def ready_listener(event : hikari.StartedEvent) -> None:
	await bot.update_presence(
		status = hikari.Status.ONLINE,
		activity = hikari.Activity(
			name = "the market",
			type = hikari.ActivityType.LISTENING
		)
	)
	bot.unsubscribe(hikari.StartingEvent, starting_listener)
	bot.unsubscribe(hikari.StartedEvent, ready_listener)


@bot.listen(hikari.StoppingEvent)
async def close_database(event : hikari.StoppedEvent) -> None:
	global db
	db.commit()
	db.close()

@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("module", description = "The module to load", type = str, required = False)
@lightbulb.command("load", "Loads an module", hidden = True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def load_module(ctx : lightbulb.Context) -> None:
	module = ctx.options.module if ctx.options.module is not None else None
	if module is None:
		await ctx.respond(f"No module provided to load!", reply = True)
		return
	try:
		bot.load_extensions(f"modules.{module}")
		await ctx.respond(f"Successfully loaded module {module}", reply = True)
	except Exception as e:
		await ctx.respond(f":warning: Couldn't load module {module}. The following exception was raised: \n```{e.__cause__ or e}```", reply = True)

@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("module", description = "The module to unload", type = str, required = False)
@lightbulb.command("unload", "Unloads a module", hidden = True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def unload_module(ctx : lightbulb.Context) -> None:
	module = ctx.options.module if ctx.options.module is not None else None
	if module is None:
		await ctx.respond(f"No module provided to unload!", reply = True)
		return
	else:
		try:
			bot.unload_extensions(f"modules.{module}")
			await ctx.respond(f"Successfully unloaded module {module}", reply = True)
		except Exception as e:
			await ctx.respond(f"Couldn't unload module {module}. The following exception was raised: \n```{e.__cause__ or e}```", reply = True)

@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("module", description = "The module to reload", type = str, required = False)
@lightbulb.command("reload", "Reloads an extension", hidden = True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def reload_module(ctx : lightbulb.Context) -> None:
	module = ctx.options.module if ctx.options.module is not None else None
	if module is None:
		await ctx.respond(f"No module provided to reload!", reply = True)
		return
	try:
		bot.reload_extensions(f"modules.{module}")
		await ctx.respond(f"Successfully reloaded module {module}", reply = True)
	except Exception as e:
		await ctx.respond(f":warning: Couldn't reload module {module}. The module has been reverted back to the previous working state if already loaded. The following exception was raised: \n```{e.__cause__ or e}```", reply = True)

@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("logout", "Shuts the bot down", aliases = ['shutdown'], hidden = True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def logout_bot(ctx : lightbulb.Context) -> None:
	await ctx.respond(f"Shutting the bot down", reply = True)
	await bot.close()

if __name__ == '__main__':
	bot.run()
