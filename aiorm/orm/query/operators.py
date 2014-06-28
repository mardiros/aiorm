##
#  Statement that are not chained, but used via parameters
#

class and_:

    def __init__(self, *statements):
        self.statements = statement

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


class greater_than:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def render_sql(self, renderer):
        return renderer.render_greater_than(self)


class greater_or_equal_than:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def render_sql(self, renderer):
        return renderer.render_greater_or_equal_than(self)


class less_than:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def render_sql(self, renderer):
        return renderer.render_less_than(self)


class less_or_equal:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def render_sql(self, renderer):
        return renderer.render_less_or_equal_than(self)
