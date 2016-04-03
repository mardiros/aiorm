""" Declaration of SQL Schema """

from .columns import Column, PrimaryKey, ForeignKey
from .relations import OneToOne, OneToMany, ManyToMany
from .types import Integer, Boolean, Timestamp, Text, String, UUID, CIText
