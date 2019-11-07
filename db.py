# coding: utf-8
from peewee import *
# import time
# from json import dumps, loads
# from uuid import uuid1
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = PrimaryKeyField(unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)
    client_name = CharField(null=True)
    phone = CharField(null=True)
    email = CharField(null=True)
    cur_stage = CharField(null=True)
    test_name = CharField(null=True)
    question_num = CharField(null=True)