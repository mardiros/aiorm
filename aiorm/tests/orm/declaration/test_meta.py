from aiorm.tests.testing import TestCase

# The main part of the meta is tested in the test_decorator.py in fact.

class MetaTestCase(TestCase):

    def test_default(self):
        from aiorm.orm.declaration.meta import db
        self.assertEqual(db, {})
        self.assertEqual(db['db'], {})
        self.assertEqual(db, {'db': {}})
        db.pop('db')
