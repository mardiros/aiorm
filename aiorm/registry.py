"""
Component registry

based on zope.interfaces

"""
# XXX a copy/paste from apium

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


def get_component(adapted_iface, original_iface=IDriver):
    """ Return a singleton object for the given interface """

    if (adapted_iface, original_iface) not in _instances:
        _instances[(adapted_iface, original_iface)] = get(adapted_iface,
                                                          original_iface)()

    return _instances[(adapted_iface, original_iface)]


def get_driver():
    """ Return the Driver Singleton """
    return get_component(IDriver)
