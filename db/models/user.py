from .. import BaseModel
from .guild import Guild

from peewee import BigIntegerField, ForeignKeyField

class User(BaseModel):
    guild = ForeignKeyField(Guild)
    userid = BigIntegerField()
    balance = BigIntegerField(default=0)
    cooldown = BigIntegerField(default=0)
    
    class Meta:
        table_name = 'users'
    