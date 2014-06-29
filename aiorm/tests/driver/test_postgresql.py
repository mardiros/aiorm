import asyncio
from unittest import mock

from aiorm.tests.testing import TestCase


class PostgresTestCase(TestCase):
    _pool = mock.Mock()

    def setUp(self):
        super().setUp()
        self._pool = mock.Mock()
        self.aiopgpool = mock.patch('aiopg.create_pool',
                                    new=self.mock_create_pool)
        self.aiopgpool.start()

    def tearDown(self):
        super().tearDown()
        self.aiopgpool.stop()

    @asyncio.coroutine
    def mock_create_pool(self, **kwargs):
        return self._pool.connect(**kwargs)

    def test_connect(self):
        @asyncio.coroutine
        def aiotest():
            from aiorm.driver.postgresql.aiopg import Driver
            yield from Driver().connect('postgresql://localhost/db')
            self._pool.connect.assert_called_with(host='localhost',
                                                  port=5432,
                                                  user='postgres',
                                                  password='secret',
                                                  database='db')
        asyncio.get_event_loop().run_until_complete(aiotest())
