from .. import BaseModel
from .guild import Guild
from  .user import User

from peewee import TextField, ForeignKeyField, BigIntegerField, BooleanField

class Raffle(BaseModel):
    guild: Guild = ForeignKeyField(Guild)
    message_id = BigIntegerField(default=None, null=True)
    channel_id = BigIntegerField(default=None)
    winner = ForeignKeyField(User, null=True)
    prize = TextField()
    end = BigIntegerField()
    fee = BigIntegerField()
    finished = BooleanField(default=False)

    class Meta:
        table_name = 'raffles'


class RaffleEntry(BaseModel):
    raffle: Raffle = ForeignKeyField(Raffle, backref='entries')
    user: User = ForeignKeyField(User, backref="raffles")

    class Meta:
        table_name = 'raffleEntries'
