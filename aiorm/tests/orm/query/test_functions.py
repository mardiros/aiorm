from unittest.mock import Mock

from aiorm.tests.testing import TestCase


class FunctionTestCase(TestCase):

    def test_utc_now(self):
        from aiorm.orm.query.functions import utc_now
        visitor = Mock()
        utc_now.render_sql(visitor)
        visitor.render_utcnow.assert_called_once_with(utc_now)

    def test_count(self):
        from aiorm.orm.query.functions import count
        visitor = Mock()
        field = Mock()
        count(field).render_sql(visitor)
        visitor.render_count.assert_called_once_with(field)
