import asyncio
from unittest import mock

from aiorm.tests.testing import TestCase
from aiorm.tests.fixtures import sample


class DialectTestCase(TestCase):

    _fixtures = [sample.SampleFixture]

    def setUp(self):
        super().setUp()
        from aiorm.orm.dialect.postgresql import Dialect
        self._dialect = Dialect()

    def test_render_get_simple_pk(self):

        self._dialect.render_get(sample.User, 1876)
        self.assertEqual(self._dialect.query, """\
SELECT {0}."created_at", {0}."email", {0}."firstname", {0}."id", {0}."lang", \
{0}."lastname", {0}."login", {0}."password"
FROM "user" AS {0}
WHERE {0}."id" = %s
""".format(sample.User.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [1876])

    def test_render_get_coumpound_pk(self):

        self._dialect.render_get(sample.UserGroup, user_id=18, group_id=76)
        self.assertEqual(self._dialect.query, """\
SELECT {0}."group_id", {0}."user_id"
FROM "user_group" AS {0}
WHERE {0}."group_id" = %s AND {0}."user_id" = %s
""".format(sample.UserGroup.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [76, 18])

    def test_render_select(self):
        self._dialect.render_select(sample.Group)
        self.assertEqual(self._dialect.query, """\
SELECT {0}."created_at", {0}."id", {0}."name"
FROM "group" AS {0}
""".format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [])

    def test_render_select_count(self):
        from aiorm import orm
        self._dialect.render_select(orm.count(sample.Group.id))
        self.assertEqual(self._dialect.query, """\
SELECT COUNT({0}."id")
FROM "group" AS {0}
""".format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [])

    def test_render_insert(self):
        group = sample.Group(name='test')
        self._dialect.render_insert(group)
        self.assertEqual(self._dialect.query, """\
INSERT INTO "group"("created_at", "name")
VALUES ((NOW() at time zone 'utc'), %s)
RETURNING "created_at", "id", "name"
""")
        self.assertEqual(self._dialect.parameters, ['test'])

    def test_render_update(self):
        user = sample.User(id=89, login='john', email='j@hn.me',
                           created_at='XXX now XXX')
        user.firstname = 'first'
        user.lastname = 'last'
        self._dialect.render_update(user)
        self.assertEqual(self._dialect.query, """\
UPDATE "user"
SET "created_at" = %s, "email" = %s, "firstname" = %s, "lang" = %s, \
"lastname" = %s, "login" = %s, "password" = %s
WHERE "id" = %s
RETURNING "created_at", "email", "firstname", "id", "lang", "lastname", \
"login", "password"
""")
        self.assertEqual(self._dialect.parameters,
                         ['XXX now XXX', 'j@hn.me', 'first', None, 'last',
                          'john', None, 89])

    def test_render_delete(self):
        user = sample.User(id=89, login='john', email='j@hn.me')
        self._dialect.render_delete(user)
        self.assertEqual(self._dialect.query, """\
DELETE FROM "user"
WHERE "id" = %s
""")
        self.assertEqual(self._dialect.parameters,
                         [89])

    def test_render_join(self):
        self._dialect._from_model = sample.User
        user_group = sample.UserGroup(user_id=89, group_id=7)
        self._dialect.render_join(user_group)
        self.assertEqual(self._dialect.query, """\
INNER JOIN  "user_group" AS {0} ON "{1}".id = "{0}".user_id
""".format(sample.UserGroup.__meta__['alias'], sample.User.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [])

    def test_render_left_join(self):
        self._dialect._from_model = sample.User
        user_group = sample.UserGroup(user_id=89, group_id=7)
        self._dialect.render_left_join(user_group)
        self.assertEqual(self._dialect.query, """\
LEFT JOIN  "user_group" AS {0} ON "{1}".id = "{0}".user_id
""".format(sample.UserGroup.__meta__['alias'], sample.User.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [])

    def test_render_where(self):
        self._dialect.render_where(sample.Group.name == 'wheel',
                                   sample.User.login == 'alice')
        self.assertEqual(self._dialect.query, """\
WHERE {}."name" = %s
  AND {}."login" = %s
""".format(sample.Group.__meta__['alias'], sample.User.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, ['wheel', 'alice'])

    def test_render_group_by(self):
        self._dialect.render_group_by(sample.Group.name, sample.User.login)
        self.assertEqual(self._dialect.query, """\
GROUP BY {}."name", {}."login"
""".format(sample.Group.__meta__['alias'], sample.User.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [])

    def test_render_order_by(self):
        self._dialect.render_order_by(sample.Group.name, sample.User.login)
        self.assertEqual(self._dialect.query, """\
ORDER BY {}."name", {}."login"
""".format(sample.Group.__meta__['alias'], sample.User.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, [])

    def test_render_equal(self):
        equal = mock.Mock()
        equal.column = sample.Group.name
        equal.value = 'staff'
        self._dialect.render_equal(equal)
        self.assertEqual(self._dialect.query,
                          '{}."name" = %s'
                          ''.format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, ['staff'])

    def test_render_greater_than(self):
        equal = mock.Mock()
        equal.column = sample.Group.name
        equal.value = 'staff'
        self._dialect.render_greater_than(equal)
        self.assertEqual(self._dialect.query,
                          '{}."name" > %s'
                          ''.format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, ['staff'])

    def test_render_greater_than_or_equal(self):
        equal = mock.Mock()
        equal.column = sample.Group.name
        equal.value = 'staff'
        self._dialect.render_greater_than_or_equal(equal)
        self.assertEqual(self._dialect.query,
                          '{}."name" >= %s'
                          ''.format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, ['staff'])

    def test_render_less_than(self):
        equal = mock.Mock()
        equal.column = sample.Group.name
        equal.value = 'staff'
        self._dialect.render_less_than(equal)
        self.assertEqual(self._dialect.query,
                          '{}."name" < %s'
                          ''.format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, ['staff'])

    def test_render_less_than_or_equal(self):
        equal = mock.Mock()
        equal.column = sample.Group.name
        equal.value = 'staff'
        self._dialect.render_less_than_or_equal(equal)
        self.assertEqual(self._dialect.query,
                          '{}."name" <= %s'
                          ''.format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, ['staff'])

    def test_render_in(self):
        in_ = mock.Mock()
        in_.column = sample.Group.name
        in_.values = ['staff']
        self._dialect.render_in(in_)
        self.assertEqual(self._dialect.query,
                          '{}."name" IN (%s)'
                          ''.format(sample.Group.__meta__['alias']))
        self.assertEqual(self._dialect.parameters, ['staff'])

    def test_render_begin_transaction(self):
        rendered = self._dialect.render_begin_transaction()
        self.assertEqual(rendered, 'begin')

    def test_render_rollback_transaction(self):
        rendered = self._dialect.render_rollback_transaction()
        self.assertEqual(rendered, 'rollback')

    def test_render_commit_transaction(self):
        rendered = self._dialect.render_commit_transaction()
        self.assertEqual(rendered, 'commit')

    def test_render_utcnow(self):
        rendered = self._dialect.render_utcnow(mock.Mock())

        self.assertEqual(rendered, "(NOW() at time zone 'utc')")
        self.assertEqual(self._dialect.query, '')
        self.assertEqual(self._dialect.parameters, [])

    def test_render_count_field(self):
        field = mock.Mock()
        field.model.__meta__ = {'alias': 'a'}
        field.name = 'my_name'
        rendered = self._dialect.render_count(field)

        self.assertEqual(rendered, 'COUNT(a."my_name")')
        self.assertEqual(self._dialect.query, '')
        self.assertEqual(self._dialect.parameters, [])


class CreateTableDialectTestCase(TestCase):

    _fixtures = [sample.SampleFixture]

    def setUp(self):
        super().setUp()
        from aiorm.orm.dialect.postgresql import CreateTableDialect
        self._dialect = CreateTableDialect()

    def test_render_create_table(self):
        self._dialect.render_create_table(sample.UserGroup)
        self.assertEqual(self._dialect.query,
                         """\
CREATE TABLE IF NOT EXISTS "user_group" (
  "group_id" int NOT NULL,
  "user_id" int NOT NULL,
  CONSTRAINT "user_group_group_id_fkey" FOREIGN KEY ("group_id")
    REFERENCES "group" ("id") MATCH SIMPLE ON UPDATE NO ACTION \
ON DELETE NO ACTION,
  CONSTRAINT "user_group_user_id_fkey" FOREIGN KEY ("user_id")
    REFERENCES "user" ("id") MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO \
ACTION
)
""")
