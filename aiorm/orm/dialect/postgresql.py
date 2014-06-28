"""

SQL Dialect of postrgresql engine

"""
from  zope.interface import implementer, Interface

from aiorm import registry
from ..query import interfaces


@implementer(interfaces.IDialect)
class Dialect:

    def __init__(self):
        self.query = ''
        self._from_model = None
        self.parameters = []

    def render_get(self, model_class, *primary_key, **primary_keys):
        meta = model_class.__meta__
        fields = ', '.join(['{}."{}"'.format(meta['alias'], col)
                            for col in meta['columns']])

        if primary_key and primary_keys:
            raise RuntimeError('args and kwargs cannot be combined here')

        if primary_key:
            if len(primary_key) > 1 or len(meta['primary_key']) > 1:
                raise RuntimeError('Cannot use args one multiple primary key')
            where_clause = '{}."{}" = %s'.format(meta['alias'], list(meta['primary_key'].keys())[0])
            self.parameters.append(primary_key[0])
        elif primary_keys:
            try:
                where_clause = []
                for pkey in meta['primary_key'].keys():
                    where_clause.append('{}."{}" = %s'.format(meta['alias'], pkey))
                    self.parameters.append(primary_keys[pkey])
            except KeyError as exc:
                raise RuntimeError('Missing primary key value %s' % exc)

            where_clause = ' AND '.join(where_clause)
        else:
            raise RuntimeError('Missing primary key value')

        self.query += ('SELECT {}\n'
                       'FROM "{}" AS {}\n'
                       'WHERE {}\n').format(fields,
                                            meta['tablename'],
                                            meta['alias'],
                                            where_clause)

    def render_select(self, model_class):
        meta = model_class.__meta__
        fields = ', '.join(['{}."{}"'.format(meta['alias'], col)
                            for col in meta['columns']])
        self._from_model = model_class
        self.query += ('SELECT {}\n'
                       'FROM "{}" AS {}\n').format(fields,
                                                   meta['tablename'],
                                                   meta['alias'])

    def render_insert(self, model):
        meta = model.__meta__
        fields = ', '.join(['"{}"'.format(col) for col in meta['columns']
            if not getattr(model.__class__, col).options.get('autoincrement')])
        values = ','.join([getattr(model, col).render_sql(self)  # defaults
            if interfaces.IFunction.providedBy(getattr(model, col))
            else '%s'
            for col in meta['columns']
            if not getattr(model.__class__, col).options.get('autoincrement')])
        all_fields = ', '.join(['"{}"'.format(col) for col in meta['columns']])
        
        self.query += ('INSERT INTO "{}"({})\n'
                       'VALUES ({})\n'
                       'RETURNING {}').format(meta['tablename'],
                                              fields,
                                              values,
                                              all_fields)
        self.parameters = [getattr(model, col) for col in meta['columns']
            if not getattr(model.__class__, col).options.get('autoincrement')
            and not hasattr(getattr(model, col), 'render_sql')]

    def render_update(self, model):
        meta = model.__meta__
        fields = ', '.join(['"{}" = %s'.format(col) for col in meta['columns']
            if not getattr(model.__class__, col).options.get('immutable')])
        all_fields = ', '.join(['"{}"'.format(col) for col in meta['columns']])
        keys = list(model.__class__.__meta__['pkv'](model).items())

        where = ','.join(['"{}" = %s'.format(key[0]) for key in keys])

        self.query += ('UPDATE "{}"\n'
                       'SET {}\n'
                       'WHERE {}\n'
                       'RETURNING {}').format(meta['tablename'], fields,
                                              where, all_fields)
        self.parameters = [getattr(model, col) for col in meta['columns']
            if not getattr(model.__class__, col).options.get('immutable')]
        self.parameters += [key[1] for key in keys]

    def render_delete(self, model):
        meta = model.__meta__
        keys = list(model.__class__.__meta__['pkv'](model).items())
        where = ','.join(['"{}" = %s'.format(key[0]) for key in keys])

        self.query += ('DELETE FROM "{}"\n'
                       'WHERE {}\n').format(meta['tablename'], where)
        self.parameters += [key[1] for key in keys]

    def _render_join(self, foreign_model_class, condition, join_type):
        meta = foreign_model_class.__meta__
        if not condition:
            condition = []
            model_meta = self._from_model.__meta__

            for key, val in meta['foreign_keys'].items():
                if val.foreign_key.model == self._from_model:
                    condition.append('"{}".{} = "{}".{}'.format(
                        model_meta['alias'],
                        val.foreign_key.name,
                        meta['alias'],
                        key))

        self._from_model.__meta__['foreign_keys']
        join_condition = '\n  AND '.join(condition)
        self.query += ('{} JOIN  "{}" AS {} '
                       'ON {}\n').format(join_type,
                                         meta['tablename'],
                                         meta['alias'],
                                         join_condition)

    def render_join(self, foreign_model_class, condition=None):
        self._render_join(foreign_model_class, condition, 'INNER')

    def render_left_join(self, foreign_model_class, condition=None):
        self._render_join(foreign_model_class, condition, 'LEFT')
        
    def render_where(self, statement, *statements, **unused):
        self.query += 'WHERE '
        statement.render_sql(self)
        for statement in statements:
            self.query += '\n  AND '
            statement.render_sql(self)

    def __render_cmp(self, field, operator):
        self.query += '{}."{}" {} %s'.format(
            field.column.model.__meta__['alias'],
            field.column.name,
            operator)
        self.parameters.append(field.value)

    def render_equal(self, field):
        self.__render_cmp(field, '=')

    def render_greater_than(self, field):
        self.__render_cmp(field, '>')

    def render_greater_or_equal_than(self, field):
        self.__render_cmp(field, '>=')

    def render_less_than(self, field):
        self.__render_cmp(field, '<')

    def render_less_or_equal_than(self, field):
        self.__render_cmp(field, '<=')

    # XXX those methods return somethink instead of righting in the query
    def render_utcnow(self, utcnow):
        return "(NOW() at time zone 'utc')"


@implementer(interfaces.ICreateTableDialect)
class CreateTableDialect:

    def __init__(self):
        self.query = None
        self.primary_key_cols = {}
        self.foreign_keys_cols = {}
        self.columns = {}
        self.constraint = []

    def render_create_table(self, model_class):
        meta = model_class.__meta__
        columns = set(meta['columns'])

        [getattr(model_class, col).render_sql(self) for col in meta['columns']]
        columns_declaration = []
        pkeys = sorted(self.primary_key_cols.keys())
        for key in pkeys:
            columns_declaration.append(self.primary_key_cols[key])
        for key in sorted(self.foreign_keys_cols.keys()):
            columns_declaration.append(self.foreign_keys_cols[key])
        for key in sorted(self.columns.keys()):
            columns_declaration.append(self.columns[key])

        if pkeys:
            columns_declaration.append('CONSTRAINT "{}_pkey" PRIMARY KEY ("{}")'
                                       ''.format(meta['tablename'],
                                                 '", "'.join(pkeys)
                                                 ))
        columns_declaration.extend(self.constraint)
        self.query = ('CREATE TABLE IF NOT EXISTS"{}" (\n'
                      '\t{}\n'
                      ')\n').format(meta['tablename'],
                                    ',\n\t'.join(columns_declaration,)
                                    )

    def _render_column(self, field):
        return '"{}" {}{}'.format(field.name,
                                  field.type.render_sql(self),
                                  '' if field.nullable else ' NOT NULL',
                                  )

    def _render_unique_constraint(self, field):
        return ('CONSTRAINT "{}_{col}" UNIQUE ("{col}")'
                '').format(field.model.__meta__['tablename'],
                           col=field.name)

    def _render_foreign_key(self, field):
        return ('CONSTRAINT "{}_{}_fkey" FOREIGN KEY ("{}")\n\t\t'
                'REFERENCES "{}" ("{}") MATCH SIMPLE '
                'ON UPDATE NO ACTION ON DELETE NO ACTION'
                '').format(field.model.__meta__['tablename'],
                           field.name,
                           field.name,
                           field.foreign_key.model.__meta__['tablename'],
                           field.foreign_key.name
                           )

    def render_primary_key(self, field):
        self.primary_key_cols[field.name] = self._render_column(field)

    def render_foreign_key(self, field):
        self.foreign_keys_cols[field.name] = self._render_column(field)
        self.constraint.append(self._render_foreign_key(field))
        if field.unique:
            self.constraint.append(self._render_unique_constraint(field))

    def render_column(self, field):
        self.columns[field.name] = self._render_column(field)
        if field.unique:
            self.constraint.append(self._render_unique_constraint(field))

    def render_integer(self, field):
        ret = 'serial' if field.autoincrement else 'int'
        return ret

    def render_timestamp(self, field):
        ret = 'timestamp'
        if not field.with_timezone:
            ret += ' without time zone'
        return ret

    def render_string(self, field):
        ret = 'character varying({})'.format(field.length)
        return ret

    def render_text(self, field):
        return 'text'
