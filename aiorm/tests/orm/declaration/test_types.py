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
        visitor.render_integer.assert_called_once_with(int)

    def test_timestamp(self):
        from aiorm.orm.declaration import types
        timestamp = types.Timestamp()
        self.assertTrue(timestamp.with_timezone)
        self.assertIsNone(timestamp.default)
        visitor = mock.Mock()
        timestamp.render_sql(visitor)
        visitor.render_timestamp.assert_called_once_with(timestamp)

    def test_string(self):
        from aiorm.orm.declaration import types
        string = types.String()
        self.assertIsNone(string.length)
        visitor = mock.Mock()
        string.render_sql(visitor)
        visitor.render_string.assert_called_once_with(string)

    def test_text(self):
        from aiorm.orm.declaration import types
        text = types.Text()
        visitor = mock.Mock()
        text.render_sql(visitor)
        visitor.render_text.assert_called_once_with(text)

    def test_citext(self):
        from aiorm.orm.declaration import types
        text = types.CIText()
        visitor = mock.Mock()
        text.render_sql(visitor)
        visitor.render_citext.assert_called_once_with(text)

    def test_uuid(self):
        from aiorm.orm.declaration import types
        text = types.UUID()
        visitor = mock.Mock()
        text.render_sql(visitor)
        visitor.render_uuid.assert_called_once_with(text)

    def test_boolean(self):
        from aiorm.orm.declaration import types
        boolean = types.Boolean()
        visitor = mock.Mock()
        boolean.render_sql(visitor)
        visitor.render_boolean.assert_called_once_with(boolean)

    def test_jsonb(self):
        from aiorm.orm.declaration import types
        jsonb = types.JSONB()
        visitor = mock.Mock()
        jsonb.render_sql(visitor)
        visitor.render_jsonb.assert_called_once_with(jsonb)
