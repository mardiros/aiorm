""" Abstract sql statements to create schema """
import asyncio
import logging

from  zope.interface import implementer, Interface

from aiorm import registry
from . import interfaces
from .statements import _Query, _NoResultQuery
from ..declaration import meta

log = logging.getLogger(__name__)


class CreateTable(_NoResultQuery):
    def render_sql(self):
        renderer = registry.get(interfaces.ICreateTableDialect)()
        renderer.render_create_table(*self._args, **self._kwargs)
        return renderer.query, []


class CreateSchema(_Query):
    def render_sql(self):
        renderer = registry.get(interfaces.ICreateTableDialect)()
        renderer.render_create_table(*self._args, **self._kwargs)
        return renderer.query, renderer.parameters
