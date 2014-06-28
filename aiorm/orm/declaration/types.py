
class SQLType:

    def __init__(self):
        self.default = None

    def render_sql(self, renderer):
        raise NotImplementedError


class Integer(SQLType):

    def __init__(self):
        super().__init__()
        self.autoincrement = None

    def render_sql(self, renderer):
        return renderer.render_integer(self)


class Timestamp(SQLType):

    def __init__(self):
        super().__init__()
        self.with_timezone = True

    def render_sql(self, renderer):
        return renderer.render_timestamp(self)


class Text(SQLType):

    def render_sql(self, renderer):
        return renderer.render_text(self)


class String(SQLType):

    def __init__(self):
        super().__init__()
        self.length = None

    def render_sql(self, renderer):
        return renderer.render_string(self)
