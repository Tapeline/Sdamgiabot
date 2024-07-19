import os

from peewee import (Model, PostgresqlDatabase,
                    IntegerField, TextField, SqliteDatabase, BooleanField)


if os.getenv("RUN_MODE") == "PROD":
    db = PostgresqlDatabase(database="database", host="postgres", port=5432,
                            user="bot_user", password="bot_db_password")
else:
    db = SqliteDatabase('sqlite.db', pragmas={'journal_mode': 'wal'})


def init():
    db.connect()
    db.create_tables([User])


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    tg_id = IntegerField()
    topics = TextField()
    already_seen = TextField()
    receive_daily = BooleanField(default=True)
