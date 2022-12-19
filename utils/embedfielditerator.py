from lightbulb import Context
from hikari import Embed

async def iterator(ctx: Context, title: str, values: list):
    embe = Embed(title=title, color=0x8bfc80)
    embeds = []
    for name, value in values:
        if len(embe.fields)==25:
            embeds.append(embe)
            embe = Embed(title=f'Page {len(embeds)+1}', color=0x8bfc80)
        embe.add_field(name=name, value=value, inline=False)
    if not embe in embeds:
        embeds.append(embe)
    await ctx.respond(embed=embeds[0], reply=True)
    for i in embeds[1:]:
        await ctx.respond(embed=i, reply=False)