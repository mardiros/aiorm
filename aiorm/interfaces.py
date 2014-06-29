from zope.interface import Attribute, Interface


class IDriver(Interface):
    """ Apium driver handle the high level api of the broker communication.
    It is expose has a singleton to be the mediator for tasks treatment.
    """
    database = Attribute(""" The connected database or None if not connected
                         """)

    def connect(self, url):
        """ coroutine that connect the driver using parameters from the
        given url """

    def cursor(self):
        """ coroutine that retrieve a cursor to execute sql query """
