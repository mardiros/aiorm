from unittest.mock import Mock

from zope.interface import implementer

from aiorm import registry
from aiorm.orm.query.interfaces import ICreateTableDialect


class DummyDialect(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = Mock()
        return cls._instance


@implementer(ICreateTableDialect)
class DummyCreateTableDialect(DummyDialect):
    _instance = None


class CreateTableDialectFixture:

    def setUp(self):
        registry.register(DummyCreateTableDialect, ICreateTableDialect)

    def tearDown(self):
        registry.unregister(DummyCreateTableDialect)
        DummyCreateTableDialect._instance = None
