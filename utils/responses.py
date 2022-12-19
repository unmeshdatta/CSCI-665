from hikari import Embed
from lightbulb import Context

POSCOLOR = 0x8bfc80
NEGCOLOR = 0xe53751

def _pos(title: str, description: str = None, url: str = None, **kwargs):
    return Embed(title=title, description=description, 
                 url=url, color=POSCOLOR,
                 **kwargs)


def _err(title: str, description: str = None, url: str = None, **kwargs):
    return Embed(title=title, description=description, 
                 url=url, color=NEGCOLOR,
                 **kwargs)

async def pos(ctx: Context, title: str, description: str = None, url: str = None, **kwargs):
    embe = _pos(title=title, description=description, 
                 url=url)
    await ctx.respond(embed=embe, reply=True, **kwargs)

async def err(ctx: Context, title: str, description: str = None, url: str = None, **kwargs):
    embe = _err(title=title, description=description, 
                 url=url)
    await ctx.respond(embed=embe, reply=True, **kwargs)
