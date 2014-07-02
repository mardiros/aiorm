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

        class IAdapter2(Interface):
            pass

        @implementer(IAdaptable)
        class Adaptable:
            pass

        @implementer(IAdapter)
        class Adapter:
            pass

        @implementer(IAdapter2)
        class Adapter2:
            pass

        self.assertRaises(NotImplementedError, registry.get, IAdapter)
        registry.register(Adapter, adapt=IAdaptable)  # introspect iface
        self.assertRaises(ValueError,
                          registry.register, Adapter, adapt=IAdaptable)
        registry.register(Adaptable, IAdaptable, adapt=IAdaptable) # explicit
        registry.register(Adapter2, adapt=Adaptable)

        # 3 "types" accepted for the adapt parameter
        self.assertEqual(registry.get(IAdapter, adapt=IAdaptable), Adapter)
        self.assertEqual(registry.get(IAdapter, adapt=Adaptable), Adapter)
        self.assertEqual(registry.get(IAdapter, adapt=Adaptable()), Adapter)

        self.assertEqual(registry.get(IAdaptable, adapt=IAdaptable), Adaptable)
        self.assertEqual(registry.get(IAdaptable, adapt=Adaptable), Adaptable)

        registry.unregister(Adapter, IAdaptable)
        self.assertRaises(NotImplementedError,
                          registry.get, IAdapter, adapt=IAdaptable)
        registry.unregister(Adapter)
        registry.unregister(Adapter2)

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

    def test_driver_connect_not_registered_db(self):
        from aiorm import registry
        self.assertRaises(RuntimeError, registry.get_driver, 'not_reg')
