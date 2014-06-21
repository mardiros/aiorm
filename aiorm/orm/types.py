
class SQLType:

    def __init__(self, nullable=True):
        self.nullable = nullable

    def accept(self, visitor):
        raise NotImplementedError


class Integer(SQLType):

    def accept(self, visitor):
        visitor.visit_integer(self)


class Timestamp(SQLType):

    def accept(self, visitor):
        visitor.visit_timestamp(self)


class Text(SQLType):

    def accept(self, visitor):
        visitor.visit_text(self)


class String(SQLType):

    def __init__(self, length, **kwargs):
        self.length = length
        super().__init__(kwargs)

    def accept(self, visitor):
        visitor.visit_string(self)
