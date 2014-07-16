from unittest.mock import Mock

from aiorm.tests.testing import TestCase


class FunctionTestCase(TestCase):

    def test_utc_now(self):
        from aiorm.orm.query.functions import utc_now
        visitor = Mock()
        utc_now.render_sql(visitor)
        visitor.render_utcnow.assert_called_with(utc_now)
