##
#  Statement that are not chained, but used via parameters
#

class and_:

    def __init__(self, *statements):
        self.statements = statements

    def render_sql(self, renderer):
        return renderer.render_and(self)


class or_(and_):

    def render_sql(self, renderer):
        return renderer.render_or(self)


class equal:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def render_sql(self, renderer):
        return renderer.render_equal(self)


class greater_than(equal):

    def render_sql(self, renderer):
        return renderer.render_greater_than(self)


class greater_than_or_equal(equal):
    def render_sql(self, renderer):
        return renderer.render_greater_than_or_equal(self)


class less_than(equal):
    def render_sql(self, renderer):
        return renderer.render_less_than(self)


class less_than_or_equal(equal):
    def render_sql(self, renderer):
        return renderer.render_less_than_or_equal(self)
