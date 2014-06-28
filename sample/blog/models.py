import asyncio

from aiorm import orm
from aiorm import registry


class Table:

    def __init__(self, **kwargs):

        for key, val in kwargs.items():
            if not hasattr(self.__class__, key):
                raise RuntimeError('Column {} not declared')
            if not isinstance(getattr(self.__class__, key), orm.Column):
                raise RuntimeError('{} is not a column'.format(key))
            setattr(self, key, val)

    def __repr__(self):
        return '<Table {} #{}>'.format(self.__class__.__name__, self.id)



@orm.table(database='sample', name='user__group')
class UserGroup(Table):
    group_id = orm.ForeignKey('group.id')
    user_id = orm.ForeignKey('user.id')


@orm.table(database='sample', name='group')
class Group(Table):
    
    id = orm.PrimaryKey(orm.Integer)
    created_at = orm.Column(orm.Timestamp)
    name = orm.Column(orm.String(255))
    users = orm.ManyToMany('user', 'user__group')


@orm.table(database='sample', name='user')
class User(Table):
    
    id = orm.PrimaryKey(orm.Integer, autoincrement=True)
    created_at = orm.Column(orm.Timestamp, default=orm.utc_now())
    login = orm.Column(orm.String(50))
    password = orm.Column(orm.String(60))
    firstname = orm.Column(orm.String(255))
    lastname = orm.Column(orm.String(255))
    email = orm.Column(orm.String(255))
    lang = orm.Column(orm.String(2))
    preferences = orm.OneToMany('user_preference.user_id')
    groups = orm.ManyToMany(Group, UserGroup)

    @classmethod
    @asyncio.coroutine
    def by_id(cls, id):
        return (yield from orm.Query(cls).filter(cls.id == id).get_one())



@orm.table(database='sample', name='preference')
class Preference(Table):

    id = orm.PrimaryKey(orm.Integer, autoincrement=True)
    created_at = orm.Column(orm.Timestamp, default=orm.utc_now())
    key = orm.Column(orm.String(50))
    type = orm.Column(orm.String(50))
    default = orm.Column(orm.Text)


@orm.table(database='sample', name='user_preference')
class UserPreference(Table):

    id = orm.PrimaryKey(orm.Integer, autoincrement=True)
    created_at = orm.Column(orm.Timestamp, default=orm.utc_now())
    user_id = orm.ForeignKey(User.id)
    preference_id = orm.ForeignKey(Preference.id)
    value = orm.Column(orm.Text)

    preference = orm.OneToOne(preference_id)
