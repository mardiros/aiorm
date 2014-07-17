import asyncio
from unittest.mock import Mock

from aiorm.tests.testing import TestCase
from aiorm.tests.fixtures import driver
from aiorm.tests.fixtures import dialect
from aiorm.tests.fixtures import sample


class GetTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):

        from aiorm.orm.query import statements as stmt
        query, parameters = stmt.Get(sample.User, 1).render_sql()
        dummy_dialect = dialect.DummyDialect()
        dummy_dialect.render_get.assert_called_once_with(sample.User, 1)


    def test_where(self):
        from aiorm.orm.query import statements as stmt
        where = stmt.Get(sample.User, 1).where
        self.assertIsInstance(where, stmt.Where)
        dummy_dialect = dialect.DummyDialect()
        condition = Mock()
        query, parameters = where(condition).render_sql(dummy_dialect)
        dummy_dialect.render_where.assert_called_once_with(condition)

    def test_run(self):

        @asyncio.coroutine
        def aiotest():

            from aiorm import registry
            from aiorm.orm.query import statements as stmt

            driver.DummyCursor.return_one = [range(3)]
            yield from registry.connect('/sample')
            group = yield from stmt.Get(sample.Group, 1).run()
            yield from registry.disconnect('sample')

            self.assertEqual(group.to_dict(),
                             {'id': 1, 'created_at': 0, 'name': 2})

        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_run_where_no_result(self):

        @asyncio.coroutine
        def aiotest():

            from aiorm import registry
            from aiorm.orm.query import statements as stmt

            driver.DummyCursor.return_one = [None]

            yield from registry.connect('/sample')
            groups = yield from stmt.Get(sample.Group, 1).where(Mock()).run()
            yield from registry.disconnect('sample')

            driver.DummyDriver.mock = driver.DummyCursor()
            self.assertIsNone(groups)

        asyncio.get_event_loop().run_until_complete(aiotest())


class SelectTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):

        from aiorm.orm.query import statements as stmt
        query, parameters = stmt.Select(sample.User).render_sql()
        dummy_dialect = dialect.DummyDialect()
        dummy_dialect.render_select.assert_called_once_with(sample.User)

    def test_where(self):
        from aiorm.orm.query import statements as stmt
        where = stmt.Select(sample.User).where
        self.assertIsInstance(where, stmt.Where)
        dummy_dialect = dialect.DummyDialect()
        condition = Mock()
        query, parameters = where(condition).render_sql(dummy_dialect)
        dummy_dialect.render_where.assert_called_once_with(condition)


    def test_join(self):
        from aiorm.orm.query import statements as stmt
        join = stmt.Select(sample.User).join
        self.assertIsInstance(join, stmt.Join)

    def test_left_join(self):
        from aiorm.orm.query import statements as stmt
        join = stmt.Select(sample.User).left_join
        self.assertIsInstance(join, stmt.LeftJoin)

    def test_run(self):

        @asyncio.coroutine
        def aiotest():

            from aiorm import registry
            from aiorm.orm.query import statements as stmt

            driver.DummyCursor.return_many = [[range(3),
                                               range(10, 13)],
                                              ]

            yield from registry.connect('/sample')
            groups = yield from (stmt.Select(sample.Group)
                                     .join(sample.User)
                                     .left_join(sample.UserPreference,
                                                sample.User.id ==
                                                sample.UserPreference.user_id)
                                     .where(Mock()).run()
                                     )
            yield from registry.disconnect('sample')

            groups = [group for group in groups]
            self.assertEqual(len(groups), 2)
            self.assertEqual(groups[0].to_dict(),
                             {'id': 1, 'created_at': 0, 'name': 2})
            self.assertEqual(groups[1].to_dict(),
                             {'id': 11, 'created_at': 10, 'name': 12})

        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_run_fetch_one_no_result(self):

        @asyncio.coroutine
        def aiotest():

            from aiorm import registry
            from aiorm.orm.query import statements as stmt

            driver.DummyCursor.return_one = [None]

            yield from registry.connect('/sample')
            groups = yield from stmt.Select(sample.Group).run(fetchall=False)
            yield from registry.disconnect('sample')

            driver.DummyDriver.mock = driver.DummyCursor()
            self.assertIsNone(groups)

        asyncio.get_event_loop().run_until_complete(aiotest())


class InsertTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):

        from aiorm.orm.query import statements as stmt
        user = sample.User(login='bob', firstname='bob')
        query, parameters = stmt.Insert(user).render_sql()
        dummy_dialect = dialect.DummyDialect()
        dummy_dialect.render_insert.assert_called_once_with(user)

    def test_run(self):

        @asyncio.coroutine
        def aiotest():

            from aiorm import registry
            from aiorm.orm.query import statements as stmt

            driver.DummyCursor.return_one = [range(3)]
            yield from registry.connect('/sample')
            group = sample.Group(name='sample')
            group = yield from stmt.Insert(group).run()
            yield from registry.disconnect('sample')
            self.assertEqual(group.to_dict(),
                             {'id': 1, 'created_at': 0, 'name': 2})

        asyncio.get_event_loop().run_until_complete(aiotest())


class UpdateTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):
        from aiorm.orm.query import statements as stmt
        user = sample.User(id=23, login='alice', firstname='alice')
        query, parameters = stmt.Update(user).render_sql()
        dummy_dialect = dialect.DummyDialect()
        dummy_dialect.render_update.assert_called_once_with(user)


class DeleteTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):
        from aiorm.orm.query import statements as stmt
        user = sample.User(id=24, login='john', firstname='john')
        query, parameters = stmt.Delete(user).render_sql()
        dummy_dialect = dialect.DummyDialect()
        dummy_dialect.render_delete.assert_called_once_with(user)


class JoinTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):
        from aiorm.orm.query import statements as stmt
        query = Mock()
        user =  Mock()
        join = stmt.Join(query)
        join(user)

        dummy_dialect = dialect.DummyDialect()
        join.render_sql(dummy_dialect)
        dummy_dialect.render_join.assert_called_once_with(user)


class LeftJoinTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):
        from aiorm.orm.query import statements as stmt
        query = Mock()
        user =  Mock()
        join = stmt.LeftJoin(query)
        join(user)

        dummy_dialect = dialect.DummyDialect()
        join.render_sql(dummy_dialect)
        dummy_dialect.render_left_join.assert_called_once_with(user)


class WhereTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_render_sql(self):
        from aiorm.orm.query import statements as stmt
        query = Mock()
        condition =  Mock()
        where = stmt.Where(query)
        where(condition)

        dummy_dialect = dialect.DummyDialect()
        where.render_sql(dummy_dialect)
        dummy_dialect.render_where.assert_called_once_with(condition)
