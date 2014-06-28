from zope.interface import implementer
from .interfaces import IFunction


@implementer(IFunction)
class utc_now:

    @classmethod
    def render_sql(cls, renderer):
        return renderer.render_utcnow(cls)
