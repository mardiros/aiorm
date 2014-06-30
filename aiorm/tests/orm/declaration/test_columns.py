from unittest import mock
from aiorm.tests.testing import TestCase
from aiorm.tests.fixtures import sample


class ColumnTestCase(TestCase):

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

    def test_equal(self):
        from aiorm import orm
        from aiorm.orm.query import operators

        class Test:
            field = orm.Column(mock.Mock)

        self.assertIsInstance(Test.field == 1, operators.equal)
        self.assertIsInstance(Test.field > 1, operators.greater_than)
        self.assertIsInstance(Test.field >= 1, operators.greater_than_or_equal)
        self.assertIsInstance(Test.field < 1, operators.less_than)
        self.assertIsInstance(Test.field <= 1, operators.less_than_or_equal)


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


class PrimaryKeyTestCase(TestCase):

    def test_primary_key_composed(self):
        from aiorm import orm

        class Test:
            field1 = orm.PrimaryKey(mock.Mock)
            field2 = orm.PrimaryKey(mock.Mock)
            field3 = orm.Column(mock.Mock)

        self.assertTrue(Test.field1.immutable)
        self.assertTrue(Test.field2.immutable)

    def test_render_sql(self):
        from aiorm import orm

        class Test:
            field = orm.PrimaryKey(mock.Mock)

        visitor = mock.Mock()
        Test.field.render_sql(visitor)
        visitor.render_primary_key.assert_called_with(Test.field)


class ForeignKeyTestCase(TestCase):

    def test_render_sql(self):
        from aiorm import orm

        class Test:
            field1 = orm.PrimaryKey(mock.Mock)

        class Test2:
            field2 = orm.ForeignKey(Test.field1)

        visitor = mock.Mock()
        Test2.field2.render_sql(visitor)
        visitor.render_foreign_key.assert_called_with(Test2.field2)