from unittest import mock
from aiorm.tests.testing import TestCase


class ColumnTestScase(TestCase):

    def test_column_all_args(self):
        from aiorm import orm
        type = mock.Mock()

        col = orm.Column('name', lambda: type,
                         immutable=True,
                         nullable=True,
                         unique=True,
                         default='x',
                         foo='bar'
                         )
        self.assertEqual(col.name, 'name')
        self.assertEqual(col.type, type)
        self.assertEqual(col.type.foo, 'bar')
        self.assertIsNone(col.model)
        self.assertTrue(col.immutable)
        self.assertTrue(col.nullable)
        self.assertTrue(col.unique)
        self.assertEqual(col.default_value, 'x')

    def test_column_simple(self):
        from aiorm import orm
        col = orm.Column(lambda: 'type')
        self.assertIsNone(col.model)
        self.assertIsNone(col.name)
        self.assertEqual(col.type, 'type')
        self.assertFalse(col.immutable)
        self.assertFalse(col.nullable)
        self.assertFalse(col.unique)
        self.assertIsNone(col.default_value)

    def test_colum_model(self):
        from aiorm import orm

        class Test:
            field = orm.Column(mock.Mock)

        self.assertEqual(Test.field.model, Test)

        test = Test()
        test.field = 'val'

        self.assertEqual(Test.field._get_model(test), 'val')
        self.assertEqual(test.field, 'val')

    def test_render_sql(self):
        from aiorm import orm

        class Test:
            field = orm.Column(mock.Mock)

        visitor = mock.Mock()
        Test.field.render_sql(visitor)
        visitor.render_column.assert_called_with(Test.field)

    def test_immutable_field(self):
        from aiorm import orm
        from aiorm.orm.declaration.columns import ImmutableFieldUpdateError

        class Test:
            field = orm.Column(mock.Mock, immutable=True)

        test = Test()
        test.field = 1
        with self.assertRaises(ImmutableFieldUpdateError):
            test.field = 2
