import asyncio
import logging

from aiorm import orm
from aiorm import registry
from aiorm.orm.dialect.postgresql import Dialect
from aiorm.orm.dialect import Get, Select, Insert, Update, Delete
from aiorm.driver.postgresql.aiopg import Driver
from aiorm.orm.dialect.postgresql import Dialect
from blog.models import User, UserPreference, Group


@asyncio.coroutine
def routine(future):

    registry.register(Driver)
    registry.register(Dialect)
    yield from registry.connect('postgresql://pg:sample@192.168.122.246:5432/sample',
                                name='sample')
    driver = registry.get_driver('sample')
    driver.scan('blog.models')
    user = yield from Get(User, 1).run()
    print (user.login)
    """
    users = yield from Select(User).left_join(UserPreference).run()
    for user in users:
    prefs = yield from user.preferences
    for pref in prefs:
        print ((yield from pref.preference).key, pref.value)
        print (user.__dict__)
    """


    groups = yield from user.groups
    for group in groups:
        print (group.name)
    
    group = yield from Get(Group, 1).run()
    users = yield from group.users
    for user in users:
        print (user.login)

    '''
    user = User(login='mylogin', password='should be encrypted',
                email='my@email.tld',
                firstname='john',
                lastname='do',
                lang='en')
    
    yield from Insert(user).run()

    #user = yield from Get(User, 4).run()
    #user.id = 3
    user.email = 'john@do.email'
    user.firstname = 'John'
    #yield from Update(user).run()

    yield from Delete(user).run()
    '''
    future.set_result(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    future = asyncio.Future()
    loop = asyncio.get_event_loop()
    asyncio.async(routine(future))
    loop.run_until_complete(future)
    loop.stop()
