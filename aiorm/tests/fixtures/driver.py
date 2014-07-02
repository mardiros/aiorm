
import asyncio

from zope.interface import implementer
from aiorm import registry
from aiorm.interfaces import IDriver


@implementer(IDriver)
class DummyDriver:
    last_url = None

    @asyncio.coroutine
    def connect(self, url):
        """ create the driver and connect from the given url """
        self.__class__.last_url = url
        self.database = url.rsplit('/', 2).pop()


class DriverFixture:

    @classmethod
    def setUpClass(cls):
        registry.register(DummyDriver)

    @classmethod
    def tearDownClass(cls):
        registry.unregister(DummyDriver)
