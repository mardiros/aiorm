""" Abstract sql statements to create schema """
import asyncio
import logging

from  zope.interface import implementer, Interface

from aiorm import registry
from . import interfaces
from .statements import _Query, _NoResultQuery
from ..declaration import meta

log = logging.getLogger(__name__)


class CreateTable(_NoResultQuery):
    def render_sql(self):
        renderer = registry.get(interfaces.ICreateTableDialect)()
        renderer.render_create_table(*self._args, **self._kwargs)
        return renderer.query, []


class CreateSchema:
    def __init__(self, database):
        try:
            self.database = database
        except KeyError  as exc:
            raise RuntimeError('Database {} not registered'.format(exc))

    @asyncio.coroutine
    def run(self, cursor=None):
        for table in meta.list_tables(self.database):
            yield from CreateTable(table).run(cursor)
