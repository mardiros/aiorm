"""
Component registry

based on zope.interfaces

"""
import asyncio

from zope.interface import interface, declarations, implementedBy
from zope.interface.adapter import AdapterRegistry

from .interfaces import IDriver

_iface_registry = AdapterRegistry()


def register(registred_type, *adapted_ifaces, adapt=IDriver):
    """ Register an adapter class for an original interface that implement
    adapted_ifaces. """
    assert registred_type, 'You need to pass an Interface'

    # deal with class->interface adapters:
    if not isinstance(adapt, interface.InterfaceClass):
        adapt = declarations.implementedBy(adapt)

    if not adapted_ifaces:
        adapted_ifaces = implementedBy(registred_type)

    for iface in adapted_ifaces:
        factory = _iface_registry.registered([adapt], iface)
        if factory is not None:
            raise ValueError('an adapter (%s) was already registered.' %
                             (factory, ))

    for iface in adapted_ifaces:
        _iface_registry.register([adapt], iface, '', registred_type)


def get(adapted_iface, original_iface=IDriver):
    """ Return registered adapter for a given class and interface. """

    if not isinstance(original_iface, interface.InterfaceClass):
        if hasattr(original_iface, '__class__'):
            original_iface = original_iface.__class__
        original_iface = declarations.implementedBy(original_iface)

    registred_type = _iface_registry.lookup1(original_iface, adapted_iface, '')
    if not registred_type:
        raise NotImplementedError('No implementation has been registered')
    return registred_type


_instances = {}


@asyncio.coroutine
def connect(url, name=None):
    """
    If name is provided, it's override the database in the url for
    the database in the code. e.g. you can have a database name which
    does not match the database name in your aiorm decorated class.
    """
    # XXX actually aiorm support only postgresql so this works,
    # but if we have to manage many connection on different
    # engine we are screwed, a lots of refactor have to be planned
    driver = get(IDriver)()
    yield from driver.connect(url)
    if name is None:
        name = url.rsplit('/', 2).pop()
    _instances[name] = driver


def get_driver(name):
    """ Return the Driver Singleton """
    try:
        return _instances[name]
    except KeyError:
        raise RuntimeError('Database {} is not registred')
