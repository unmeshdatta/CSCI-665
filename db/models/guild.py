from .. import BaseModel

from peewee import BigIntegerField

class Guild(BaseModel):
    gid = BigIntegerField()
    raffle_channel = BigIntegerField(default=None, null=True)

    class Meta:
        table_name = 'guilds'
