import asyncio

from .meta import db
from .columns import BaseField
from ..query import Select


class BaseRelation(BaseField):

    def _get_model_cls(self, model):
        ret = super()._get_model_cls(model)
        self._resolve_foreign_keys()
        return ret

    def _resolve_foreign_keys(self):
        raise NotImplementedError


class OneToOne(BaseRelation):

    def __init__(self, foreign_key, **option):
        super().__init__(None, **option)
        self.foreign_key = foreign_key

    def render_sql(self, renderer):
        renderer.render_one_to_one(self)

    def _resolve_foreign_keys(self):
        if isinstance(self.foreign_key, str):
            meta = self.model.__meta__
            table, field = self.foreign_key.split('.', 1)
            try:
                self.foreign_key = getattr(db[meta['database']][table], field)
            except KeyError:
                pass # The model has not been scanned

    @asyncio.coroutine
    def _get_model(self, model):
        if model not in self.data:
            self._resolve_foreign_keys()
            fkey = self.foreign_key.foreign_key
            value = self.model.__meta__['pkv'](model)[fkey.name]
            data = (yield from Select(fkey.model).where(fkey == value)
                                                 .run(fetchall=False))
            self.data[model] = data
        return self.data[model]

    def __set__(self, model, value):
        if not isinstance(value, self.foreign_key.foreign_key.model):
            raise RuntimeError('Invalid value for relation {}.{}.{}'.format(
                self.model.__meta__['database'],
                self.model.__meta__['tablename'], self.name))
        value = getattr(value, self.foreign_key.foreign_key.name)
        setattr(model, self.foreign_key.name, value)


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


class ManyToMany(BaseRelation):
    """
    Describe a relation using 3 tables.
     * the table where the ManyToMany relation is described
     * the foreing model wich will be iterable in the model instance
     * the secondary containing foreign keys between the two other tables
    """

    def __init__(self, foreign_model, secondary):
        super().__init__(None)
        self.foreign_model = foreign_model
        self.secondary = secondary

    def render_sql(self, renderer):
        renderer.render_many_to_many(self)

    def _resolve_foreign_keys(self):
        meta = self.model.__meta__
        try:
            if isinstance(self.foreign_model, str):
                self.foreign_model = db[meta['database']][self.foreign_model]
            if isinstance(self.secondary, str):
                self.secondary = db[meta['database']][self.secondary]
        except KeyError:
            pass # The model has not been scanned

    @asyncio.coroutine
    def _get_model(self, model):
        self._resolve_foreign_keys()
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
