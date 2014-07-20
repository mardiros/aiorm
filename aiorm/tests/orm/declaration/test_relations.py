import asyncio
from unittest import mock

from aiorm.tests.testing import TestCase
from aiorm.tests.fixtures import sample
from aiorm.tests.fixtures import driver


class BasicTestCase(TestCase):

    def test_onetoone(self):
        from aiorm import orm
        visitor = mock.Mock()
        relation = orm.OneToOne('x.y')
        self.assertEqual(relation.foreign_key, 'x.y')
        relation.render_sql(visitor)
        visitor.render_one_to_one.assert_called_once_with(relation)

    def test_onetomany(self):
        from aiorm import orm
        visitor = mock.Mock()
        relation = orm.OneToMany('x.y')
        self.assertEqual(relation.foreign_key, 'x.y')
        relation.render_sql(visitor)
        visitor.render_one_to_many.assert_called_once_with(relation)

    def test_manytomany(self):
        from aiorm import orm
        visitor = mock.Mock()
        relation = orm.ManyToMany('x', 'y')
        self.assertEqual(relation.foreign_model, 'x')
        self.assertEqual(relation.secondary, 'y')

        relation.render_sql(visitor)
        visitor.render_many_to_many.assert_called_once_with(relation)


class SchemaTestCase(TestCase):
    """ tests that require that __meta__ is set """

    _fixtures = [sample.SampleFixture, driver.DriverFixture]

    @asyncio.coroutine
    def aioSetUp(self):
        from aiorm import registry
        from aiorm.orm.dialect.postgresql import Dialect, CreateTableDialect
        registry.register(Dialect)
        registry.register(CreateTableDialect)

        yield from registry.connect('/sample')
        #driver.DummyDriver.mock = mock.Mock()

    @asyncio.coroutine
    def aioTearDown(self):
        from aiorm import registry
        from aiorm.orm.dialect.postgresql import Dialect, CreateTableDialect
        registry.unregister(Dialect)
        registry.unregister(CreateTableDialect)
        yield from registry.disconnect('sample')

    def test_one_to_one_resolve_foreign_keys(self):
        from aiorm.tests.fixtures.sample import (UserPreference, User,
                                                 Preference)
        # does not changed
        self.assertEqual(UserPreference.preference.foreign_key, Preference.id)
        # is casted from string to model
        self.assertEqual(UserPreference.user.foreign_key, User.id)

    def test_one_to_one_get_model(self):
        @asyncio.coroutine
        def aiotest():
            from datetime import datetime
            from aiorm.tests.fixtures.sample import Preference, UserPreference

            userpref = UserPreference(user_id=1, preference_id=1, value='1')
            created_at = datetime.now()
            driver.DummyCursor.return_one = [
                [created_at, 'default', 1, 'name', 'str'],
            ]
            pref = yield from userpref.preference
            self.assertIsInstance(pref, Preference)
            self.assertEqual(pref.id, 1)
            self.assertEqual(pref.created_at, created_at)
            self.assertEqual(pref.key, 'name')
            self.assertEqual(pref.type, 'str')
            self.assertEqual(pref.default, 'default')

            driver.DummyCursor.return_one = [None]
            pref = yield from userpref.preference
            self.assertIsNone(pref)

        asyncio.get_event_loop().run_until_complete(aiotest())


    def test_one_to_many_resolve_foreign_keys(self):
        from aiorm.tests.fixtures.sample import User, UserPreference
        self.assertEqual(User.preferences.foreign_key, UserPreference.id)

    def test_one_to_many_get_model(self):
        @asyncio.coroutine
        def aiotest():
            from datetime import datetime
            from aiorm.tests.fixtures.sample import User, UserPreference

            user = User(id=1, email='alice@nd.bob', login='alice')
            driver.DummyCursor.return_many = [[]]
            prefs = [pref for pref in (yield from user.preferences)]
            self.assertEqual(prefs, [])

            created_at = datetime.now()
            driver.DummyCursor.return_many = [
                [[created_at, 10, 20, 1, 'one'],
                 [created_at, 11, 21, 1, 'two'],
                 ]
            ]
            prefs = [pref for pref in (yield from user.preferences)]
            self.assertEqual(len(prefs), 2)
            self.assertIsInstance(prefs[0], UserPreference)
            self.assertIsInstance(prefs[1], UserPreference)
            self.assertEqual(prefs[0].created_at, created_at)
            self.assertEqual(prefs[1].created_at, created_at)
            self.assertEqual(prefs[0].user_id, 1)
            self.assertEqual(prefs[1].user_id, 1)
            self.assertEqual(prefs[0].preference_id, 20)
            self.assertEqual(prefs[1].preference_id, 21)
            self.assertEqual(prefs[0].id, 10)
            self.assertEqual(prefs[1].id, 11)
            self.assertEqual(prefs[0].value, 'one')
            self.assertEqual(prefs[1].value, 'two')

        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_many_to_many_resolve_foreign_keys(self):
        from aiorm.tests.fixtures.sample import User, Group, UserGroup
        self.assertEqual(User.groups.foreign_model, Group)
        self.assertEqual(User.groups.secondary, UserGroup)

        self.assertEqual(Group.users.foreign_model, User)
        self.assertEqual(Group.users.secondary, UserGroup)

    def test_many_to_many_get_model(self):
        @asyncio.coroutine
        def aiotest():

            from datetime import datetime
            from aiorm.tests.fixtures.sample import User, Group

            created_at = datetime.now()
            user = User(id=1, email='alice@nd.bob', login='alice')
            driver.DummyCursor.return_many = [[]]
            groups = [group for group in (yield from user.groups)]
            self.assertEqual(groups, [])

            driver.DummyCursor.return_many = [
                [[created_at, 1, 'user'],
                 [created_at, 2, 'staff']
                 ]
            ]
            groups = [group for group in (yield from user.groups)]
            self.assertEqual(len(groups), 2)
            self.assertIsInstance(groups[0], Group)
            self.assertIsInstance(groups[1], Group)
            self.assertEqual(groups[0].created_at, created_at)
            self.assertEqual(groups[1].created_at, created_at)
            self.assertEqual(groups[0].id, 1)
            self.assertEqual(groups[1].id, 2)
            self.assertEqual(groups[0].name, 'user')
            self.assertEqual(groups[1].name, 'staff')

        asyncio.get_event_loop().run_until_complete(aiotest())
