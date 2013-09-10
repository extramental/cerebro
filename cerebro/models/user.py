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

    class Factory(object):
        def __init__(self, request):
            self.request = request

        def __getitem__(self, name):
            user = DBSession.query(User).filter(User.name == name).first()
            if user is None:
                raise KeyError(name)
            return user


    class ProjectFactory(object):
        def __init__(self, request):
            self.request = request

        def __getitem__(self, name):
            user = User.Factory(self.request)[name]
            from .project import Project

            class _Factory(object):
                __parent__ = user

                def __getitem__(self, name):
                    o = DBSession.query(Project).filter(
                        User.id == self.__parent__.id,
                        Project.name == name
                    ).first()
                    if o is None:
                        raise KeyError(id)
                    return o

            return _Factory()
