from weakref import WeakKeyDictionary

from .meta import db
from .columns import Column, BaseColumn


class PrimaryKey(Column):
    """ Declare Primary key """

    def __init__(self, *args, **options):
        super().__init__(*args, immutable=True, **options)

    def render_sql(self, renderer):
        return renderer.render_primary_key(self)

    def __get_pkv(model_cls):
        def get_pkv(model):
            return {key: getattr(model, key)
                    for key in model_cls.__meta__['primary_key'].keys()
                    }
        return get_pkv

    def _get_model_cls(self, model_cls):
        # class access
        super()._get_model_cls(model_cls)
        if not hasattr(self.model, '__meta__'):
            # XXX not available until venusian passed
            return self

        if self not in self.model.__meta__['primary_key'].values():
            self.model.__meta__['primary_key'][self.name] = self
            self.model.__meta__['pkv'] = PrimaryKey.__get_pkv(model_cls)
        return self


class ForeignKey(BaseColumn):
    """ Declare a foreign key """

    def __init__(self, *args, **options):
        self.nullable = options.pop('nullable', False)
        self.unique = options.pop('unique', False)
        super().__init__(*args, **options)

        self.foreign_key =  None
        self.options = options
        if not isinstance(self.type, str):
            self.type, self.foreign_key = self.type.type, self.type
            self.set_options()
        self.data = WeakKeyDictionary()

    def set_options(self):
        for key, val in self.options.items():
            setattr(self.type, key, val)

    def render_sql(self, renderer):
        return renderer.render_foreign_key(self)

    def _get_model(self, model):
        return self.data.get(model, self.options.get('default'))

    def _get_model_cls(self, model_cls):
        super()._get_model_cls(model_cls)

        if not self.foreign_key:
            meta = self.model.__meta__
            table, field = self.type.split('.', 1)
            self.foreign_key = getattr(db[meta['database']][table], field)
            self.type = self.foreign_key.type.__class__()
            self.set_options()

        self.model.__meta__['foreign_keys'][self.name] = self
        return self
