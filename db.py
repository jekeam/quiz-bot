# coding: utf-8
from peewee import *
# import time
# from json import dumps, loads
# from uuid import uuid1
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('bot_manager', user='root', password='131189_Ak', host='127.0.0.1', port=3306)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = PrimaryKeyField(unique=True)
    role = CharField(null=False, default='client')
    phone = CharField(null=False)
    email = CharField(null=False)
    date_start = IntegerField(null=False, default=get_trunc_sysdate())
    date_end = IntegerField(null=True)
