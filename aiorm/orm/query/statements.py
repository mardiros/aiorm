""" Abstract sql statements to query schema """
import asyncio
import logging

from  zope.interface import implementer

from aiorm import registry
from . import interfaces


log = logging.getLogger(__name__)


class _Query:

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._child = None

    def __getattr__(self, key):
        """
        Use zope.interface for easy extensability.
        If you want to had your own statement, register your own interface,
        with your own implementation in aiorm registry.
        """
        iface = 'I' + ''.join(txt.capitalize() for txt in key.split('_'))
        iface = getattr(interfaces, iface)
        self._child = registry.get(iface)(self)
        return self._child

    @asyncio.coroutine
    def run(self, cursor=None, fetchall=True):

        @asyncio.coroutine
        def wrapped(cursor):
            sql_statement = self.render_sql()
            log.debug('{} % {!r}'.format(*sql_statement))
            yield from cursor.execute(*sql_statement)
            return ((yield from cursor.fetchall())
                    if fetchall else (yield from cursor.fetchone()))

        if cursor:
            return (yield from wrapped(cursor))
        else:
            driver = registry.get_driver(self._args[0].__meta__['database'])
            with (yield from driver.cursor()) as cursor:
                return (yield from wrapped(cursor))


class _NoResultQuery(_Query):

    @asyncio.coroutine
    def run(self, cursor=None):
        @asyncio.coroutine
        def wrapped(cursor):
            sql_statement = self.render_sql()
            log.debug('{!r} % {!r}'.format(*sql_statement))
            yield from cursor.execute(*sql_statement)
            return True

        if cursor:
            return (yield from wrapped(cursor))
        else:
            driver = registry.get_driver(self._args[0].__meta__['database'])
            with (yield from driver.cursor()) as cursor:
                return (yield from wrapped(cursor))


class _SingleResultQuery(_Query):

    @asyncio.coroutine
    def run(self, cursor=None):
        row = yield from super().run(fetchall=False, cursor=cursor)
        if row is None:
            return None
        model = self._args[0]()
        for idx, col in enumerate(model.__meta__['columns']):
            setattr(model, model.__meta__['attributes'][col], row[idx])
        return model


class _ManyResultQuery(_Query):

    @asyncio.coroutine
    def run(self, cursor=None, fetchall=True):

        def to_model(row):
            if row is None:
                return None
            model = self._args[0]()
            for idx, col in enumerate(model.__meta__['columns']):
                setattr(model, model.__meta__['attributes'][col], row[idx])
            return model

        def iter_models(rows): # XXX Can't mix yield and yield from
            for row in rows:
                yield to_model(row)

        rows = yield from super().run(fetchall=fetchall, cursor=cursor)
        return iter_models(rows) if fetchall else to_model(rows)


class Get(_SingleResultQuery):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_get(*self._args, **self._kwargs)
        if self._child:
            self._child.render_sql(renderer)
        return renderer.query, renderer.parameters


class Select(_ManyResultQuery):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_select(*self._args, **self._kwargs)
        if self._child:
            self._child.render_sql(renderer)
        return renderer.query, renderer.parameters


class Insert(_Query):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_insert(*self._args, **self._kwargs)
        return renderer.query, renderer.parameters

    @asyncio.coroutine
    def run(self, cursor=None):
        row = yield from super().run(fetchall=False, cursor=cursor)
        if row is None:
            return None
        model = self._args[0]
        for idx, col in enumerate(model.__meta__['columns']):
            setattr(model, col, row[idx])
        return model


class Update(Insert):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_update(*self._args, **self._kwargs)
        return renderer.query, renderer.parameters


class Delete(_NoResultQuery):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_delete(*self._args, **self._kwargs)
        return renderer.query, renderer.parameters


class Statement:

    def __init__(self, query):
        self._args = None
        self._kwargs = None
        self._query = query
        self._child = None

    def __getattr__(self, key):
        """
        Use zope.interface for easy extensability.
        If you want to had your own statement, register your own interface,
        with your own implementation in aiorm registry.
        """
        iface = ['I'] + [word.capitalize() for word in  key.split('_')]
        iface = getattr(interfaces, ''.join(iface))
        self._child = registry.get(iface)(self._query)
        return self._child

    def __call__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        return self

    @asyncio.coroutine
    def run(self, *args, **kwargs):
        return (yield from self._query.run(*args, **kwargs))


@implementer(interfaces.IJoin)
class Join(Statement):

    def render_sql(self, renderer):
        renderer.render_join(*self._args, **self._kwargs)
        if self._child:
            self._child.render_sql(renderer)
        return renderer.query, renderer.parameters


@implementer(interfaces.ILeftJoin)
class LeftJoin(Statement):

    def render_sql(self, renderer):
        renderer.render_left_join(*self._args, **self._kwargs)
        if self._child:
            self._child.render_sql(renderer)
        return renderer.query, renderer.parameters



@implementer(interfaces.IWhere)
class Where(Statement):

    def render_sql(self, renderer):
        renderer.render_where(*self._args, **self._kwargs)
        if self._child:
            self._child.render_sql(renderer)
        return renderer.query, renderer.parameters


registry.register(Where, interfaces.IWhere)
registry.register(Join, interfaces.IJoin)
registry.register(LeftJoin, interfaces.ILeftJoin)
