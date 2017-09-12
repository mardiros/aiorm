import asyncio
from unittest.mock import Mock

from aiorm.tests.testing import TestCase
from aiorm.tests.fixtures import driver
from aiorm.tests.fixtures import dialect
from aiorm.tests.fixtures import sample


class TransactionTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 dialect.DialectFixture,
                 ]

    def test_transaction(self):

        @asyncio.coroutine
        def aiotest():

            from aiorm import registry
            from aiorm.orm import Transaction

            yield from registry.connect('/sample')

            transaction = Transaction('sample')
            self.assertIsInstance(transaction.driver, driver.DummyDriver)
            self.assertEqual(transaction.driver.database, 'sample')
            yield from registry.disconnect('sample')
        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_transaction_begin(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm import Transaction
            from aiorm.orm import interfaces

            yield from registry.connect('/sample')

            cursor = registry.get(interfaces.IDialect)()
            cursor.configure_mock(**{'render_begin_transaction.return_value':
                                          'begin_transaction'})

            transaction = Transaction('sample')
            yield from transaction.begin()
            cursor.render_begin_transaction.assert_called_once_with()
            self.assertEqual(driver.DummyCursor.last_query,
                             'begin_transaction')

            yield from registry.disconnect('sample')
        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_transaction_commit(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm import Transaction
            from aiorm.orm import interfaces

            yield from registry.connect('/sample')

            cursor = registry.get(interfaces.IDialect)()
            cursor.configure_mock(**{'render_commit_transaction.return_value':
                                          'commit_transaction'})

            transaction = yield from Transaction('sample').begin()
            yield from transaction.commit()
            cursor.render_commit_transaction.assert_called_once_with()
            self.assertEqual(driver.DummyCursor.last_query,
                             'commit_transaction')

            yield from registry.disconnect('sample')
        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_transaction_rollback(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm import Transaction
            from aiorm.orm import interfaces

            yield from registry.connect('/sample')

            cursor = registry.get(interfaces.IDialect)()
            cursor.configure_mock(
                **{'render_rollback_transaction.'
                   'return_value': 'rollback_transaction'})

            transaction = yield from Transaction('sample').begin()
            yield from transaction.rollback()
            cursor.render_rollback_transaction.assert_called_once_with()
            self.assertEqual(driver.DummyCursor.last_query,
                             'rollback_transaction')

            yield from registry.disconnect('sample')
        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_transaction_execute(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm import Transaction
            from aiorm.orm import interfaces

            yield from registry.connect('/sample')

            transaction = yield from Transaction('sample').begin()
            yield from transaction.execute('dummy_query')
            self.assertEqual(driver.DummyCursor.last_query,
                             'dummy_query')

            yield from registry.disconnect('sample')
        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_transaction_fetchone(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm import Transaction
            from aiorm.orm import interfaces

            yield from registry.connect('/sample')
            driver.DummyCursor.return_one = ['one']

            transaction = yield from Transaction('sample').begin()
            result = yield from transaction.fetchone()
            self.assertEqual(result, 'one')
            yield from registry.disconnect('sample')
        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_transaction_fetchmany(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry
            from aiorm.orm import Transaction
            from aiorm.orm import interfaces

            yield from registry.connect('/sample')
            driver.DummyCursor.return_many = [[('one',), ('two',)]]

            transaction = yield from Transaction('sample').begin()
            result = yield from transaction.fetchall()
            self.assertEqual(result, [('one',), ('two',)])
            yield from registry.disconnect('sample')
        asyncio.get_event_loop().run_until_complete(aiotest())
