from unittest import mock

from aiorm.tests.testing import TestCase
from aiorm.tests.fixtures import driver
from aiorm.tests.fixtures import sample

# The main part of the meta is tested in the test_decorator.py in fact.

class MetaTestCase(TestCase):

    _fixtures = [sample.SampleFixture,
                 driver.DriverFixture,
                 ]

    def test_default(self):
        from aiorm.orm.declaration.meta import db

        self.assertEqual(db,
                         {'sample': {'group': sample.Group,
                                     'preference': sample.Preference,
                                     'user': sample.User,
                                     'user_group': sample.UserGroup,
                                     'user_preference': sample.UserPreference
                                     }})
        self.assertEqual(db['db'], {})
        self.assertEqual(db,
                         {'db': {},
                          'sample': {'group': sample.Group,
                                     'preference': sample.Preference,
                                     'user': sample.User,
                                     'user_group': sample.UserGroup,
                                     'user_preference': sample.UserPreference
                                     }})
        db.pop('db')

    def test_list_tables(self):
        from aiorm.orm.declaration.meta import list_tables

        tables = list_tables('sample')
        self.assertEqual(set(tables),
                         {sample.Group,
                          sample.User,
                          sample.UserGroup,
                          sample.Preference,
                          sample.UserPreference})
        self.assertGreater(tables.index(sample.UserGroup),
                           tables.index(sample.User))
        self.assertGreater(tables.index(sample.UserGroup),
                           tables.index(sample.Group))
        self.assertGreater(tables.index(sample.UserPreference),
                           tables.index(sample.Preference))
        self.assertGreater(tables.index(sample.UserPreference),
                           tables.index(sample.User))

    def test_list_all_tables(self):
        from aiorm.orm.declaration.meta import list_all_tables
        tables = list_all_tables()
        self.assertEqual(set(tables.keys()), {'sample'})