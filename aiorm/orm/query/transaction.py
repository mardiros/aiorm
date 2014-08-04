import asyncio
import logging

from aiorm import registry
from . import interfaces

log = logging.getLogger(__name__)


class Transaction(object):

    def __init__(self, database):
        self.driver = registry.get_driver(database)
        self.connection = None
        self.cursor = None

    @asyncio.coroutine
    def begin(self, timeout=None):
        self.connection = yield from self.driver.acquire()
        self.cursor = yield from self.connection.cursor(timeout)
        log.info('begin transaction #{}'.format(id(self)))
        renderer = registry.get(interfaces.IDialect)()
        stmt = renderer.render_begin_transaction()
        yield from self.cursor.execute(stmt)
        return self

    def _release(self):
        log.info('transaction #{} release connection'.format(id(self)))
        self.driver.release(self.connection)
        self.connection = None
        self.cursor = None

    @asyncio.coroutine
    def commit(self):
        try:
            if not self.cursor:
                raise RuntimeError('transaction #{} not begun'.format(id(self)))
            log.info('commiting transaction #{}'.format(id(self)))
            renderer = registry.get(interfaces.IDialect)()
            stmt = renderer.render_commit_transaction()
            yield from self.cursor.execute(stmt)
        finally:
            self._release()

    @asyncio.coroutine
    def rollback(self):
        try:
            if not self.cursor:
                raise RuntimeError('transaction #{} not begun'.format(id(self)))
            log.warning('rolling back transaction #{}'.format(id(self)))
            renderer = registry.get(interfaces.IDialect)()
            stmt = renderer.render_rollback_transaction()
            yield from self.cursor.execute(stmt)
        finally:
            self._release()

    # Proxy cursor coroutines

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        if not self.cursor:
            yield from self.begin()
        return (yield from self.cursor.execute(*args, **kwargs))

    def fetchone(self, *args, **kwargs):
        return self.cursor.fetchone(*args, **kwargs)  # return the coroutine

    def fetchall(self, *args, **kwargs):
        return self.cursor.fetchall(*args, **kwargs)  # return the coroutine
