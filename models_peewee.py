from peewee import *
from datetime import datetime

db = SqliteDatabase('my_database17.db', pragmas={'foreign_keys': 1})


class ModelBase(Model):
    class Meta:
        database = db


class Users(ModelBase):
    user_name = CharField(unique=True)
    role = CharField()
    email = CharField(unique=True)
    full_name = CharField()
    created_at = DateTimeField(default=datetime.now())
    enabled = BooleanField(default=True)

    class Meta:
        table_name = 'users'


class Categories(ModelBase):
    name = CharField(unique=True)

    class Meta:
        table_name = 'categories'


class Projects(ModelBase):
    name = CharField()
    prefix = CharField(unique=True)
    description = TextField()

    class Meta:
        table_name = 'projects'


class Types(ModelBase):
    prefix = CharField(unique=True)
    name = CharField()
    description = TextField()
    category = ForeignKeyField(Categories, backref='types')
    project = ForeignKeyField(Projects, backref='types')

    class Meta:
        table_name = 'types'


class Items(ModelBase):
    local_id = CharField()
    global_id = CharField(unique=True)
    type = ForeignKeyField(Types, backref='items')
    set_key = ForeignKeyField(Types, null=True, backref='items')
    locked_by = ForeignKeyField(Users, null=True, backref='items')

    class Meta:
        table_name = 'items'


class Fields(ModelBase):
    description = TextField()
    name = CharField()

    class Meta:
        table_name = 'fields'


class Status(ModelBase):
    name = CharField()

    class Meta:
        table_name = 'status'


class Versions(ModelBase):
    item_id = ForeignKeyField(Items, backref='items')
    fields = ForeignKeyField(Fields, backref='versions', unique=True)
    number = IntegerField(default=1)
    created_at = DateTimeField(default=datetime.now())
    user = ForeignKeyField(Users, backref='items')
    status = ForeignKeyField(Status, backref='status')
    justification = TextField()

    class Meta:
        table_name = 'versions'


class RelationsTypes(ModelBase):
    name = CharField()

    class Meta:
        table_name = 'relations_types'


class Relations(ModelBase):
    parent_id = ForeignKeyField(Items, backref='relations')
    child_id = ForeignKeyField(Items, backref='relations')
    type_id = ForeignKeyField(RelationsTypes, backref='relations')

    class Meta:
        table_name = 'relations'


def initialize_db():
    db.connect()
    db.create_tables([Users, Categories, Types, Projects, Items, Fields,
                     Versions, Relations, Status, RelationsTypes], safe=True)
    db.close()
