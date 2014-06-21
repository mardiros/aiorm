from zope.interface import Attribute, Interface


class IDriver(Interface):
    """ Apium driver handle the high level api of the broker communication.
    It is expose has a singleton to be the mediator for tasks treatment.
    """

    settings = Attribute("""A dict like object that store driver settings
                         """)

    def from_url(cls, url):
        """ create the driver from the given url """
