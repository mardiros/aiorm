import asyncio
import importlib
from urllib.parse import urlparse

from zope.interface import implementer
import aiopg

from aiorm.interfaces import IDriver


@implementer(IDriver)
class Driver:
    """ Apium driver handle the high level api of the broker communication.
    It is expose has a singleton to be the mediator for tasks treatment.
    """

    def __init__(self):
        self.pool = None

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

    def cursor(self):
        return self.pool.cursor()  # return the coroutine
