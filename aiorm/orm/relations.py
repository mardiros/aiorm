import asyncio

from .decorators import db
from .dialect import Select
from .columns import BaseColumn


class OneToOne(BaseColumn):

    def __init__(self, foreign_key, **option):
        super().__init__(None, **option)
        self.foreign_key = foreign_key

    def accept(self, visitor):
        visitor.visit_one_to_one(self)

    def __eq__(self, value):
        return equal(self, value)

    def _resolve_foreign_keys(self):
        meta = self.model.__meta__
        if isinstance(self.foreign_key, str):
            table, field = self.foreign_key.split('.', 1)
            self.foreign_key = getattr(db[meta['database']][table], field)
        
    @asyncio.coroutine
    def _get_model(self, model):
        self._resolve_foreign_keys()
        fkey = self.foreign_key.foreign_key
        value = self.model.__meta__['pkv'](model)[fkey.name]
        return (yield from Select(fkey.model).where(fkey == value)
                                             .run(many=False))

    def __set__(self, model, value):
        raise NotImplementedError


class OneToMany(OneToOne):

    def render_sql(self, renderer):
        renderer.render_one_to_many(self)

    @asyncio.coroutine
    def _get_model(self, model):
        self._resolve_foreign_keys()
        fkey = self.foreign_key
        value = self.model.__meta__['pkv'](model)[fkey.foreign_key.name]
        return (yield from Select(fkey.model).where(fkey == value)
                                             .run())

    def __set__(self, model, value):
        raise TypeError('Cannot set a value for OneToMany, must append/remove')


class ManyToMany(BaseColumn):

    def __init__(self, foreign_model, secondary):
        super().__init__(None)
        self.foreign_model = foreign_model
        self.secondary = secondary

    def accept(self, visitor):
        visitor.visit_many_to_many(self)

    @asyncio.coroutine
    def _get_model(self, model):
        condition = [(getattr(self.secondary, name) ==
                      getattr(model, foreign_model.foreign_key.name)
                      )
                     for (name, foreign_model) in
                        self.secondary.__meta__['foreign_keys'].items()
                     if foreign_model.foreign_key.model == model.__class__]

        return (yield from Select(self.foreign_model)
                .join(self.secondary)
                .where(*condition).run())

    def __set__(self, model, value):
        raise NotImplementedError

    def __eq__(self, value):
        return equal(self, value)

