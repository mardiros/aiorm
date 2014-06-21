""" Abstract sql statements """
import asyncio

from  zope.interface import implementer, Interface

from aiorm import registry
from . import interfaces


@implementer(interfaces.IQuery)
class Query:

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._child = None

    def __getattr__(self, key):
        iface = 'I' + ''.join(txt.capitalize() for txt in key.split('_'))
        iface = getattr(interfaces, iface)
        self._child = registry.get(iface)(self)
        return self._child

    @asyncio.coroutine
    def run(self, many=True):
        driver = registry.get_driver()
        with (yield from driver.pool.cursor()) as cur:
            sql_statement = self.render_sql()
            print (sql_statement[0], '%', sql_statement[1])
            yield from cur.execute(*sql_statement)
            return ((yield from cur.fetchall())
                    if many else (yield from cur.fetchone())
                    )


class _SingleResultQuery(Query):

    @asyncio.coroutine
    def run(self):
        row = yield from super().run(many=False)
        model = self._args[0]()
        for idx, col in enumerate(model.__meta__['columns']):
            setattr(model, col, row[idx])
        return model


class _ManyResultQuery(Query):

    @asyncio.coroutine
    def run(self, many=True):

        def to_model(row):
            model = self._args[0]()
            for idx, col in enumerate(model.__meta__['columns']):
                setattr(model, col, row[idx])
            return model
            

        def iter_models(rows): # XXX Can't mix yield and yield from
            for row in rows:
                yield to_model(row)

        if (len(self._args) > 1):
            self._many = self._args[1]            
        rows = yield from super().run(many=many)
        return iter_models(rows) if many else to_model(rows)


@implementer(interfaces.IGet)
class Get(_SingleResultQuery):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_get(*self._args, **self._kwargs)
        if self._child:
            self._child.render_sql(renderer)
        return renderer.query, renderer.parameters


@implementer(interfaces.ISelect)
class Select(_ManyResultQuery):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_select(*self._args, **self._kwargs)
        if self._child:
            self._child.render_sql(renderer)
        return renderer.query, renderer.parameters


@implementer(interfaces.IInsert)
class Insert(Query):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_insert(*self._args, **self._kwargs)
        return renderer.query, renderer.parameters

    @asyncio.coroutine
    def run(self):
        row = yield from super().run(many=False)
        model = self._args[0]
        for idx, col in enumerate(model.__meta__['columns']):
            setattr(model, col, row[idx])
        return model


@implementer(interfaces.IUpdate)
class Update(Insert):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_update(*self._args, **self._kwargs)
        return renderer.query, renderer.parameters


@implementer(interfaces.IDelete)
class Delete(Query):

    def render_sql(self):
        renderer = registry.get(interfaces.IDialect)()
        renderer.render_delete(*self._args, **self._kwargs)
        return renderer.query, renderer.parameters

    @asyncio.coroutine
    def run(self):
        driver = registry.get_driver()
        with (yield from driver.pool.cursor()) as cur:
            sql_statement = self.render_sql()
            print (sql_statement[0], '%', sql_statement[1])
            yield from cur.execute(*sql_statement)
            return True


@implementer(interfaces.IStatement)
class Statement:

    def __init__(self, query):
        self._args = None
        self._kwargs = None
        self._query = query
        self._child = None

    def __getattr__(self, key):
        iface = getattr(interfaces, 'I' + key.capitalize())
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


registry.register(Query)
registry.register(Statement)

registry.register(Get, interfaces.IGet)
registry.register(Select, interfaces.ISelect)
registry.register(Insert, interfaces.IInsert)
registry.register(Update, interfaces.IUpdate)
registry.register(Delete, interfaces.IDelete)

registry.register(Where, interfaces.IWhere)
registry.register(Join, interfaces.IJoin)
registry.register(LeftJoin, interfaces.ILeftJoin)
