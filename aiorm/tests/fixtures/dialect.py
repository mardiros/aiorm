from unittest.mock import Mock

from zope.interface import implementer

from aiorm import registry
from aiorm.orm.query.interfaces import IDialect, ICreateTableDialect


class BaseDummyDialect(object):

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = Mock()
        return cls._instance


@implementer(IDialect)
class DummyDialect(BaseDummyDialect):
    _instance = None


@implementer(ICreateTableDialect)
class DummyCreateTableDialect(BaseDummyDialect):
    _instance = None


class CreateTableDialectFixture:

    def setUp(self):
        registry.register(DummyCreateTableDialect, ICreateTableDialect)

    def tearDown(self):
        registry.unregister(DummyCreateTableDialect)
        DummyCreateTableDialect._instance = None


class DialectFixture:

    def setUp(self):
        registry.register(DummyDialect, IDialect)

    def tearDown(self):
        registry.unregister(DummyDialect)
        DummyDialect._instance = None
