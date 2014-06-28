from weakref import WeakKeyDictionary

from ..query import operators



class ImmutableFieldUpdateError(Exception):
    def __init__(self, model, column):
        super().__init__("You can't update a field declared immutable ({}.{} = {})"
                         ''.format(model.__class__.__name__,
                                   column.name,
                                   column.data.get(model)))


class BaseColumn:
    """
    Python descriptor class used to represent every column or relation.
    """

    def __init__(self, *args, **options):
        try:
            self.name, self.type = args
        except ValueError:
            self.name = None
            self.type = args[0]

        self.model = None
        self.immutable = options.pop('immutable', False)

    def _get_model(self, mode):
        raise NotImplementedError

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
        raise NotImplementedError

    def __eq__(self, value):
        return operators.equal(self, value)

    def __gt__(self, value):
        return operators.greater_than(self, value)

    def __gte__(self, value):
        return operators.greater_or_equal_than(self, value)

    def __lt__(self, value):
        return operators.less_than(self, value)

    def __lte__(self, value):
        return operators.less_or_equal_than(self, value)

    def __repr__(self):
        return '<{} {}.{}>'.format(self.__class__.__name__,
                                   self.model.__name__,
                                   self.name)

    def render_sql(self, renderer):
        raise NotImplementedError


class Column(BaseColumn):

    def __init__(self, *args, **options):
        self.nullable = options.pop('nullable', False)
        self.unique = options.pop('unique', False)
        self.default_value = options.pop('default', None)
        super().__init__(*args, **options)
        self.type = self.type()
        for key, val in options.items():
            setattr(self.type, key, val)
        self.data = WeakKeyDictionary()

    def _get_model(self, model):
        return self.data.get(model, self.default_value)

    def __set__(self, model, value):

        if (self.immutable and
            self.data.get(model, value) != value
            ):
            raise ImmutableFieldUpdateError(model, self)

        self.data[model] = value

    def render_sql(self, renderer):
        return renderer.render_column(self)
