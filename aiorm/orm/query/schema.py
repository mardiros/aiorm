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
            self.database = meta.db[database]
        except KeyError  as exc:
            raise RuntimeError('Database {} not registered'.format(exc))

    def list_tables(self):
        """ Get the database table in the correct order for the creation """
        tables_list = []

        def add_table(table):
            for foreign_key in table.__meta__['foreign_keys'].values():
                if table != foreign_key.foreign_key.model:
                    add_table(foreign_key.foreign_key.model)

            if table not in tables_list:
                tables_list.append(table)

        [add_table(table) for table in self.database.values()]

        return tables_list

    @asyncio.coroutine
    def run(self):
        for table in self.list_tables():
            yield from CreateTable(table).run()
