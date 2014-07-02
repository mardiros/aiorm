import asyncio
import unittest


class TestCase(unittest.TestCase):
    _fixtures = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fixtures_instances = []

    @classmethod
    def setupClass(cls):
        [fixture.setUpClass() for fixture in cls._fixtures
         if hasattr(fixture, 'setUpClass')]

    @classmethod
    def tearDownClass(cls):
        [fixture.tearDownClass() for fixture in reversed(cls._fixtures)
         if hasattr(fixture, 'tearDownClass')]

    def setUp(self):
        self._fixtures_instances = [fixture()
                                    for fixture in self._fixtures
                                    if hasattr(fixture, 'setUp')]
        [fixture.setUp()
         for fixture in self._fixtures_instances]
        if hasattr(self, 'aioSetUp'):
            asyncio.get_event_loop().run_until_complete(self.aioSetUp())


    def tearDown(self):
        if hasattr(self, 'aioTearDown'):
            asyncio.get_event_loop().run_until_complete(self.aioTearDown())
        [fixture.tearDown()
         for fixture in reversed(self._fixtures_instances)]
        self._fixtures_instances = []
