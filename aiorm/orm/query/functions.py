from zope.interface import implementer
from .interfaces import IFunction


@implementer(IFunction)
class utc_now:

    @classmethod
    def render_sql(cls, renderer):
        return renderer.render_utcnow(cls)

@implementer(IFunction)
class count:

    def __init__(self, field):
        self.field = field

    def render_sql(self, renderer):
        return renderer.render_count(self.field)
