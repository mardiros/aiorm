from  zope.interface import Interface

class IDialect(Interface):
    """ render a sql query """


class IQuery(Interface):
    """ First SQL Statement of a sql query """

    def __init__(self, *args, **kwargs):
        """ Store parameter that will be consumed in the run statement """

    def __getattr__(self, key):
        """ Store the next statement "key" for the query.
        Key are search in the registry index with a conversion of the
        method name to an interface name to improve redability.
        "group_by" => "IGroupBy".
        Following statement shoud are IStatement child.
        """

    def run(self):
        """ An asyncio coroutine that run the sql query and return its result
        """
        

class IGet(IQuery):
    """ Select Statement that retrieve one record as a model using its
    primary key.

    :param *args:
        args[0] contain the model class to retrieve
        args[1] can be the primary key value in case there is only one value
    :param **kwargs:
        keys are fieldname of the primary key, values are desired keys.
    """

    def run(self):
        """ Retrieve the model
        """


class IInsert(IQuery):
    """ Insert Statement that insert one model in the database 

    :param *args:
        args[0] contain the model instance to instert

    """

    def run(self):
        """ Coroutine that save the model and update it with stored fields.
        """


class IUpdate(IQuery):
    """ Update Statement that update one model

    :param *args:
        args[0] contain the model instance to instert
    """

    def run(self):
        """ Coroutine that save the model and update it with stored fields.
        """


class IDelete(IQuery):
    """ Delete Statement that delete one model

    :param *args:
        args[0] contain the model instance to instert
    """

    def run(self):
        """ Coroutine that delete the model.
        """


class ISelect(IQuery):
    """ Select Statement that retrieve multiple models """


class IUpdateMany(IQuery):
    """ Update many rows in one query """


class IInsertMany(IQuery):
    """ Insert many rows in one query """


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
