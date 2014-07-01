from unittest import mock

from aiorm.tests.testing import TestCase


class DummyModule:

    def __init__(self, name):
        self.__name__ = name


class TableDecoratorTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.venusian = mock.patch('venusian.attach', new=self._mock_attach)
        self.venusian.start()

    def tearDown(self):
        super().tearDown()
        self.venusian.stop()
        self.wrapped = None
        self.callback = None
        self.category = None

    def _mock_attach(self, wrapped, callback, category):
        self.wrapped = wrapped
        self.callback = callback
        self.category = category

    def test_table(self):
        from aiorm import orm
        from aiorm.orm.declaration.meta import db

        oldcounter = orm.table._counter

        @orm.table(database='db0', name='table1', collation='fr_FR.UTF8')
        class Table:
            id = orm.PrimaryKey(orm.Integer)
            name = orm.Column(orm.String)

        self.assertEqual(self.category, 'aiorm')
        self.assertEqual(self.wrapped, Table)
        self.assertEqual(orm.table._counter, oldcounter)
        self.callback(None, None, None)
        self.assertEqual(orm.table._counter, oldcounter + 1)
        self.assertEqual(Table, db['db0']['table1'])
        meta = Table.__meta__.copy()
        self.assertTrue(callable(meta.pop('pkv')))
        self.assertEqual(meta,
                         {'alias': 't{}'.format(oldcounter),
                          'collation': 'fr_FR.UTF8',
                          'columns': ['id', 'name'],
                          'database': 'db0',
                          'foreign_keys': {},
                          'primary_key': {'id': Table.id},
                          'tablename': 'table1'})
        db.pop('db0')  # cleanUp


class ScanTestCase(TestCase):

    def _mock_import_module(self, module):
        self.imported_module.append(module)
        return DummyModule(module)

    def test_scan(self):
        from aiorm import orm
        from aiorm.orm.declaration.meta import db
        orm.scan('aiorm.tests.fixtures.sample')
        from aiorm.tests.fixtures import sample
        self.assertEqual(db,
                         {'sample': {'user': sample.User,
                                     'group': sample.Group,
                                     'user_group': sample.UserGroup,
                                     'preference': sample.Preference,
                                     'user_preference': sample.UserPreference,
                                     }})
        db.pop('sample')

    def test_scan_many(self):
        from aiorm import orm

        import_module = mock.patch('importlib.import_module',
                                        new=self._mock_import_module)
        import_module.start()
        self.imported_module = []

        orm.scan('mod1', 'mod2')
        self.assertEqual(self.imported_module, ['mod1', 'mod2'])

        import_module.stop()
        delattr(self, 'imported_module')
