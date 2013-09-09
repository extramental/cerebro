import json

from sqlalchemy import Table, MetaData, Column, Integer
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import ColumnElement, select, func
from sqlalchemy.types import UserDefinedType, to_instance, String, Integer

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from sqlalchemy.types import UserDefinedType

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class IdMixin(object):
    """
    A mixin for entities that want an ID primary key.
    """
    id = Column(Integer, primary_key=True, nullable=False)

    @classmethod
    def by_id(cls, id):
        """
        Retrieve an entity by its primary key.
        """
        try:
            return DBSession.query(cls).filter(cls.id == id).one()
        except (NoResultFound, MultipleResultsFound):
            return None


class PGJson(UserDefinedType):
    def __init__(self, encoding="utf-8"):
        self.encoding = encoding

    def get_col_spec(self):
        return "json"

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, str) or value is None:
                return value
            else:
                return json.dumps(value, encoding=self.encoding)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None and isinstance(value, str):
                return json.loads(value)
            else:
                return value
        return process


class PGCompositeElement(ColumnElement):
    def __init__(self, base, field, type_):
        ColumnElement.__init__(self)
        self.base = base
        self.field = field
        self.type = to_instance(type_)


@compiles(PGCompositeElement)
def _compile_pgelem(expr, compiler, **kw):
    return '(%s).%s' % (compiler.process(expr.base, **kw), expr.field)


class PGCompositeType(UserDefinedType):
    def __init__(self, typemap):
        self.typemap = typemap

    class comparator_factory(UserDefinedType.Comparator):
        def __getattr__(self, key):
            try:
                type_ = self.type.typemap[key]
            except KeyError:
                raise KeyError("Type '%s' doesn't have an attribute: '%s'" % (self.type, key))

            return PGCompositeElement(self.expr, key, type_)
