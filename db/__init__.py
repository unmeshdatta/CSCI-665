from time import time
from peewee import AutoField, Model, Proxy, IntegerField
from playhouse.sqlite_ext import SqliteExtDatabase


db = Proxy()


def init_db(db_url, safe=True) -> SqliteExtDatabase:
    global db
    db.initialize(SqliteExtDatabase(db_url))
    db.connect()

    if safe:
        from .models import __all__
        tables = db.get_tables()
        for i in __all__:
            i: BaseModel
            if i._meta.table.__name__ not in tables:
                i.create_table()
                print(f"Creating table for {i._meta.table.__name__}")
    return db


class BaseModel(Model):

    id = AutoField()
    time = IntegerField(default=time)

    class Meta:
        database = db


