import lightbulb
import hikari

from utils.module import Module

handler_plugin = Module('Handler')


@handler_plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        embe = hikari.Embed(
            title=f"Something went wrong dsuring invocation of command `{event.context.command.name}`", 
            description=f"`{event.exception.__cause__}`")
        try:
            await event.context.respond(embed=embe, reply=True)
        except:
            pass
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception
   

    if isinstance(event.exception, lightbulb.errors.MissingRequiredPermission) or isinstance(exception, lightbulb.NotOwner):
        embe = hikari.Embed(title=f"You don't have the required permissions to use this command!", color=0xe53751)
    elif isinstance(event.exception, lightbulb.NotEnoughArguments):
        embe = hikari.Embed(title=f"Not enough arguments!\nRun `!help {event.context.command.name}` to learn how to use this command", color=0xe53751)
    elif isinstance(event.exception, lightbulb.errors.ConverterFailure):
        embe = hikari.Embed(title=f"Invalid argument passed!\nRun `!help {event.context.command.name}` to learn how to use this command", color=0xe53751)
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        embe = hikari.Embed(title=f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.")
    elif isinstance(exception, lightbulb.MissingRequiredPermission):
        embe = hikari.Embed(f"You do not have permissions to run this command. You require {exception.missing_perms} to run this command")
    else:
        raise exception
    
    await event.context.respond(embed=embe, reply=True)

def load(bot : lightbulb.BotApp) -> None:
	bot.add_plugin(handler_plugin)

def unload(bot : lightbulb.BotApp) -> None:
	bot.remove_plugin(handler_plugin)
