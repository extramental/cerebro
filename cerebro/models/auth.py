from sqlalchemy import *

from . import *

class User(Base, IdMixin):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    pwhash = Column(String, nullable=False)

    __table_args__ = (
        Index("users_lower_name", func.lower(name), unique=True),
        Index("users_lower_email", func.lower(email), unique=True),
    )

