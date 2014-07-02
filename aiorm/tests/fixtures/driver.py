
import asyncio
from unittest import mock

from zope.interface import implementer
from aiorm import registry
from aiorm.interfaces import IDriver


class DummyCursor:
    last_query = None
    last_parameters = None
    # set many query results in those vars
    return_many = [None,]
    return_one = [None]

    @asyncio.coroutine
    def execute(self, query, parameters):
        DummyCursor.last_query = query
        DummyCursor.last_parameters = parameters

    @asyncio.coroutine
    def fetchone(self):
        return DummyCursor.return_one.pop(0)

    @asyncio.coroutine
    def fetchall(self):
        return DummyCursor.return_many.pop(0)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


@implementer(IDriver)
class DummyDriver:
    last_url = None
    connected = False
    mock = DummyCursor()

    @asyncio.coroutine
    def connect(self, url):
        """ create the driver and connect from the given url """
        self.__class__.last_url = url
        self.__class__.connected = True
        self.database = url.rsplit('/', 2).pop()

    @asyncio.coroutine
    def disconnect(self):
        self.__class__.connected = False

    @asyncio.coroutine
    def cursor(self):
        return self.__class__.mock


class DriverFixture:

    @classmethod
    def setUpClass(cls):
        registry.register(DummyDriver)

    @classmethod
    def tearDownClass(cls):
        registry.unregister(DummyDriver)
