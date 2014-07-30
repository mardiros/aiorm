from weakref import WeakKeyDictionary
import copy

from ..query import operators
from .meta import db


class ImmutableFieldUpdateError(Exception):
    def __init__(self, model, column):
        super().__init__("You can't update a field declared immutable ({}.{} = {})"
                         ''.format(model.__class__.__name__,
                                   column.name,
                                   column.data.get(model)))


class BaseField:
    """ The descriptor base class to declare column and relation """

    def __init__(self, *args):
        try:
            self.name, self.type = args
        except ValueError:
            self.name = None
            self.type = args[0]

        self.model = None
        self.data = WeakKeyDictionary()

    def _get_model(self, mode):
        raise NotImplementedError('{} does not implement _get_model'
                                  ''.format(self.__class__.__name__))

    def _get_model_cls(self, model_cls):
        # class access
        if not self.model:
            self.model = model_cls
        if not self.name:  # populate the name if not present
            for key, val in model_cls.__dict__.items():
                if val is self:
                    self.name = key
                    break
        return self

    def __get__(self, model, cls):
        if model:
            return self._get_model(model)
        return self._get_model_cls(cls)

    def __set__(self, model, value):
        raise NotImplementedError('{} does not implement __set__'
                                  ''.format(self.__class__.__name__))


class BaseColumn(BaseField):
    """
    Python descriptor class used to represent every column or relation.
    """

    def __init__(self, *args, nullable=False, unique=False, immutable=False,
                 primary_key=False):
        super().__init__(*args)
        self.nullable = nullable
        self.unique = unique
        self.immutable = immutable
        self.primary_key = primary_key

    def _get_model_cls(self, model_cls):
        # class access
        super()._get_model_cls(model_cls)

                                   # XXX not available until venusian passed
        if not self.primary_key or not hasattr(self.model, '__meta__'):
            return self

        # Here is for Primary Key Only
        def get_pkv(model_cls):
            def get_pkv(model):
                return {key: getattr(model, key)
                        for key in model_cls.__meta__['primary_key'].keys()
                        }
            return get_pkv

        if self.name not in self.model.__meta__['primary_key']:
            self.model.__meta__['primary_key'][self.name] = self
            self.model.__meta__['pkv'] = get_pkv(model_cls)

        return self

    def __set__(self, model, value):

        if (self.immutable and
            self.data.get(model, value) != value
            ):
            raise ImmutableFieldUpdateError(model, self)

        self.data[model] = value

    def __eq__(self, value):
        return operators.equal(self, value)

    def __gt__(self, value):
        return operators.greater_than(self, value)

    def __ge__(self, value):
        return operators.greater_than_or_equal(self, value)

    def __lt__(self, value):
        return operators.less_than(self, value)

    def __le__(self, value):
        return operators.less_than_or_equal(self, value)

    def __repr__(self):
        return '<{} {}.{}>'.format(self.__class__.__name__,
                                   self.model.__name__,
                                   self.name)

    def render_sql(self, renderer):
        raise NotImplementedError('{} does not implement render_sql'
                                  ''.format(self.__class__.__name__))


class Column(BaseColumn):
    """ Standard way to declare a column """

    def __init__(self, *args, **options):
        self.default_value = options.pop('default', None)
        self.autofield = options.get('autoincrement', False)
        base_column_kw = {}
        for key in ('nullable', 'immutable', 'unique', 'primary_key'):
            base_column_kw[key] = options.pop(key, False)

        super().__init__(*args, **base_column_kw)
        self.type = self.type()
        for key, val in options.items():
            setattr(self.type, key, val)

    def _get_model(self, model):
        return self.data.get(model, self.default_value)

    def render_sql(self, renderer):
        return renderer.render_column(self)


class PrimaryKey(Column):
    """ Convenient way to declare Primary key """

    def __init__(self, *args, **options):
        super().__init__(*args, primary_key=True, immutable=True, **options)

    def render_sql(self, renderer):
        return renderer.render_primary_key(self)


class ForeignKey(BaseColumn):
    """ Declare a foreign key """

    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self.default_value = options.pop('default', None)
        self.autofield = options.get('autoincrement', False)
        self.nullable = options.pop('nullable', False)
        self.unique = options.pop('unique', False)

        self.foreign_key =  None
        self.options = options
        if not isinstance(self.type, str):
            self.type, self.foreign_key = self.type.type, self.type
            self.set_options()

    def set_options(self):
        for key, val in self.options.items():
            setattr(self.type, key, val)
        if hasattr(self.type, 'autoincrement'):
            self.type = copy.copy(self.type)
            self.type.autoincrement = False

    def render_sql(self, renderer):
        return renderer.render_foreign_key(self)

    def _get_model(self, model):
        return self.data.get(model, self.options.get('default'))

    def _get_model_cls(self, model_cls):
        super()._get_model_cls(model_cls)
        if not hasattr(self.model, '__meta__'):
            # XXX not available until venusian passed
            return self

        if not self.foreign_key:
            meta = self.model.__meta__
            table, field = self.type.split('.', 1)
            try:
                self.foreign_key = getattr(db[meta['database']][table], field)
            except KeyError as exc:
                raise RuntimeError('Table {} is not registred in database {}'
                                   ''.format(table, meta['database']))

            self.type = self.foreign_key.type.__class__()
            self.set_options()

        self.model.__meta__['foreign_keys'][self.name] = self
        return self

    def __repr__(self):
        return '<{} {}{}.{}>'.format(self.__class__.__name__,
                                   '(PK) ' if self.primary_key else '',
                                   self.model.__name__,
                                   self.name)
