import asyncio
from unittest import mock

from aiorm.tests.testing import TestCase


class TypesTestCase(TestCase):

    def test_sqltype(self):
        from aiorm.orm.declaration import types
        abstract = types.SQLType()
        self.assertIsNone(abstract.default)
        self.assertRaises(NotImplementedError, abstract.render_sql, None)

    def test_integer(self):
        from aiorm.orm.declaration import types
        int = types.Integer()
        self.assertIsNone(int.autoincrement)
        self.assertIsNone(int.default)
        visitor = mock.Mock()
        int.render_sql(visitor)
        visitor.render_integer.assert_called_with(int)

    def test_timestamp(self):
        from aiorm.orm.declaration import types
        timestamp = types.Timestamp()
        self.assertTrue(timestamp.with_timezone)
        self.assertIsNone(timestamp.default)
        visitor = mock.Mock()
        timestamp.render_sql(visitor)
        visitor.render_timestamp.assert_called_with(timestamp)

    def test_string(self):
        from aiorm.orm.declaration import types
        string = types.String()
        self.assertIsNone(string.length)
        visitor = mock.Mock()
        string.render_sql(visitor)
        visitor.render_string.assert_called_with(string)

    def test_text(self):
        from aiorm.orm.declaration import types
        text = types.Text()
        visitor = mock.Mock()
        text.render_sql(visitor)
        visitor.render_text.assert_called_with(text)
