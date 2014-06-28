from  zope.interface import Interface

class IDialect(Interface):
    """ render a sql query """


class ICreateTableDialect(Interface):
    """ render a sql query for sql schema generation """


class IStatement(Interface):
    """ An interface that build a query for a specific engine """


class IJoin(IStatement):
    """ Join Statement """


class ILeftJoin(IStatement):
    """ Join Statement """


class IWhere(IStatement):
    """ A Where clause statement """


class IGroupBy(IStatement):
    """ A Where clause statement """


class IOrderBy(IStatement):
    """ A Where clause statement """


class ILimit(IStatement):
    """ A Where clause statement """


class IFunction(Interface):
    """ A SQL Function """
