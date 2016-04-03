import asyncio
from unittest.mock import Mock

from aiorm.tests.testing import TestCase
from aiorm.tests.fixtures import driver
from aiorm.tests.fixtures import dialect
from aiorm.tests.fixtures import sample


class CreateTableTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.CreateTableDialectFixture,
                 ]

    def test_render_sql(self):
        from aiorm.orm.query.schema import CreateTable

        table = object()

        dummy_dialect = dialect.DummyCreateTableDialect()

        stmt = CreateTable(table)
        query, param = stmt.render_sql()
        self.assertEqual(dummy_dialect.query, query)
        self.assertEqual(param, [])
        dummy_dialect.render_create_table.assert_called_once_with(table)

    def test_run(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm.query.schema import CreateTable
            dummy_dialect = dialect.DummyCreateTableDialect()
            yield from registry.connect('/sample')
            yield from CreateTable(sample.Group).run()
            dummy_dialect.render_sql.assert_called_once()
            # last query is a mock, we just ensure that a query has been
            # executed, not that the query is valid, this is a dialect test
            self.assertIsNotNone(driver.DummyCursor.last_query)
            yield from registry.disconnect('sample')

        asyncio.get_event_loop().run_until_complete(aiotest())


class CreateSchemaTestCase(TestCase):
    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.CreateTableDialectFixture,
                 ]

    def test_run(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm.query.schema import CreateSchema
            dummy_dialect = dialect.DummyCreateTableDialect()
            yield from registry.connect('/sample')
            yield from CreateSchema('sample').run()
            dummy_dialect.render_sql.assert_called()
            # last query is a mock, we just ensure that at least, a query
            # has been executed, not that the query is valid, this is a
            # dialect test
            self.assertIsNotNone(driver.DummyCursor.last_query)
            yield from registry.disconnect('sample')

        asyncio.get_event_loop().run_until_complete(aiotest())
