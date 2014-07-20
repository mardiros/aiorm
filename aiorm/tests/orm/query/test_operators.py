from unittest.mock import Mock

from aiorm.tests.testing import TestCase


class OperatorTestCase(TestCase):

    def test_and(self):
        from aiorm.orm.query.operators import and_
        visitor = Mock()
        p1, p2, p3 = object(), object(), object()
        stmt = and_(p1, p2, p3)
        self.assertEqual(stmt.statements, (p1, p2, p3))
        stmt.render_sql(visitor)
        visitor.render_and.assert_called_once_with(stmt)

    def test_or(self):
        from aiorm.orm.query.operators import or_
        visitor = Mock()
        p1, p2, p3 = object(), object(), object()
        stmt = or_(p1, p2, p3)
        self.assertEqual(stmt.statements, (p1, p2, p3))
        stmt.render_sql(visitor)
        visitor.render_or.assert_called_once_with(stmt)

    def test_equal(self):
        from aiorm.orm.query.operators import equal
        visitor = Mock()
        column, value = Mock(), Mock()
        stmt = equal(column, value)
        self.assertEqual(stmt.column, column)
        self.assertEqual(stmt.value, value)
        stmt.render_sql(visitor)
        visitor.render_equal.assert_called_once_with(stmt)

    def test_greater_than(self):
        from aiorm.orm.query.operators import greater_than
        visitor = Mock()
        column, value = Mock(), Mock()
        stmt = greater_than(column, value)
        self.assertEqual(stmt.column, column)
        self.assertEqual(stmt.value, value)
        stmt.render_sql(visitor)
        visitor.render_greater_than.assert_called_once_with(stmt)

    def test_greater_than_or_equal(self):
        from aiorm.orm.query.operators import greater_than_or_equal
        visitor = Mock()
        column, value = Mock(), Mock()
        stmt = greater_than_or_equal(column, value)
        self.assertEqual(stmt.column, column)
        self.assertEqual(stmt.value, value)
        stmt.render_sql(visitor)
        visitor.render_greater_than_or_equal.assert_called_once_with(stmt)

    def test_less_than(self):
        from aiorm.orm.query.operators import less_than
        visitor = Mock()
        column, value = Mock(), Mock()
        stmt = less_than(column, value)
        self.assertEqual(stmt.column, column)
        self.assertEqual(stmt.value, value)
        stmt.render_sql(visitor)
        visitor.render_less_than.assert_called_with(stmt)

    def test_less_than_or_equal(self):
        from aiorm.orm.query.operators import less_than_or_equal
        visitor = Mock()
        column, value = Mock(), Mock()
        stmt = less_than_or_equal(column, value)
        self.assertEqual(stmt.column, column)
        self.assertEqual(stmt.value, value)
        stmt.render_sql(visitor)
        visitor.render_less_than_or_equal.assert_called_once_with(stmt)
