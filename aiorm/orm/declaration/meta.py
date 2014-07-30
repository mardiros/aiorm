import logging
from collections import defaultdict

log =logging.getLogger(__name__)

db = defaultdict(dict)
"""
Store all meta data of every registred db in a dict

meta data are also available in the "__meta__" attribute of every model.
"""

def register(database, tablename, table):
    log.info('Register table "{}"."{}"'.format(database, tablename))
    db[database][tablename] = table


def list_tables(database):
    """ Get the database table in the correct order for the creation """
    tables_list = []

    def add_table(table):
        for foreign_key in table.__meta__['foreign_keys'].values():
            if table != foreign_key.foreign_key.model:
                add_table(foreign_key.foreign_key.model)

        if table not in tables_list:
            tables_list.append(table)

    [add_table(table) for table in db[database].values()]

    return tables_list


def list_all_tables():
    return {dbname: list_tables(dbname) for dbname in db}
