import asyncio
import importlib
from urllib.parse import urlparse

from zope.interface import implementer
import venusian
import aiopg

from aiorm.interfaces import IDriver


@implementer(IDriver)
class Driver:
    """ Apium driver handle the high level api of the broker communication.
    It is expose has a singleton to be the mediator for tasks treatment.
    """

    def __init__(self):
        self.pool = None
        self.database = None
        self.tables = {}

    # def close(self):
    #    aiopg ???

    @asyncio.coroutine
    def connect(self, url):
        """ create the driver and connect from the given url """
        url = urlparse(url)
        if url.scheme not in ('postgresql', 'aiopg+postgresql'):
            raise ValueError('Invalid scheme')

        self.database = url.path[1:]
        self.pool = yield from aiopg.create_pool(
            host=url.hostname or 'localhost',
            port=url.port or 5432,
            user=url.username or 'postgres',
            password=url.password or 'secret',
            database=self.database)

    # Move me in a base class
    def register_table(self, database, table):
        """
        """
        if database != self.database:  # I handle only my database ??
            return
        
        if table.__meta__['tablename'] in self.tables:
            raise RuntimeError('Table name {} has been registered twice'
                               ''.format(table.__meta__['tablename']))
        self.tables[table.__meta__['tablename']] = table

    def scan(self, *modules):

        scanner = venusian.Scanner(driver=self)
        for mod in modules:
            scanner.scan(importlib.import_module(mod))
