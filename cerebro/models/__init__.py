from sqlalchemy import Column, Integer
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sqlalchemy.ext.declarative import declarative_base

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


class Json(UserDefinedType):
    def get_col_spec(self):
        return "JSON"
