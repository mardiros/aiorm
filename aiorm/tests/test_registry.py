import asyncio
import unittest

from .testing import TestCase
from .fixtures.driver import DriverFixture, DummyDriver


class TestRegistry(TestCase):

    def test_registry(self):

        from zope.interface import Interface, implementer
        from aiorm import registry

        class IAdaptable(Interface):
            pass

        class IAdapter(Interface):
            pass

        @implementer(IAdapter)
        class Adapter:
            pass

        registry.register(Adapter, adapt=IAdaptable)
        self.assertRaises(NotImplementedError, registry.get, IAdapter)
        self.assertEqual(registry.get(IAdapter, adapt=IAdaptable), Adapter)
        registry.unregister(IAdapter, IAdaptable)
        self.assertRaises(NotImplementedError,
                          registry.get, IAdapter, adapt=IAdaptable)


class TestDriver(TestCase):

    _fixtures = [DriverFixture]

    def test_driver_connect_noname(self):

        @asyncio.coroutine
        def aiotest():

            from aiorm import registry

            driver = yield from registry.connect('protocol://host/db')
            self.assertEqual(DummyDriver.last_url, 'protocol://host/db')
            self.assertEqual(driver.database, 'db')
            self.assertEqual(registry.get_driver('db'), driver)
            registry._drivers.pop('db')
            DummyDriver.last_url = None

        asyncio.get_event_loop().run_until_complete(aiotest())

    def test_driver_connect_withname(self):

        @asyncio.coroutine
        def aiotest():
            from aiorm import registry

            driver = yield from registry.connect('protocol://host/db',
                                                 name='other')
            self.assertEqual(DummyDriver.last_url, 'protocol://host/db')
            self.assertEqual(driver.database, 'db')
            self.assertEqual(registry.get_driver('other'), driver)
            registry._drivers.pop('other')
            DummyDriver.last_url = None

        asyncio.get_event_loop().run_until_complete(aiotest())

