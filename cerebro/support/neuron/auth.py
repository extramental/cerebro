from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings
from pyramid.request import Request
from pyramid_beaker import session_factory_from_settings

from beaker.session import Session

from cerebro.models import DBSession, Base
from cerebro.models.user import User
from cerebro.models.project import Project, ProjectACLEntry, Doc

from neuron.auth import DENY, READER, WRITER


def cerebro_session_auth_policy_factory(config_file):
    class CerebroSessionAuthPolicy(object):
        _config_file = config_file

        """
        An auth policy for Neuron. This code does not get called inside the Cerebro
        application -- instead, Neuron runs this code to perform auth.
        """
        def __init__(self, application):
            settings = get_appsettings(self._config_file)

            engine = engine_from_config(settings, "sqlalchemy.")
            DBSession.configure(bind=engine)
            Base.metadata.bind = engine

            self.session_factory = session_factory_from_settings(settings)

        def authenticate(self, request):
            session = self.session_factory(Request({
                "HTTP_COOKIE": str(request.cookies)
            }))

            user = User.by_id(session.get("identity_id", None))

            if user is None:
                return None

            return user.id

        def authorize(self, doc_id):
            doc = Doc.by_id(doc_id)

            if doc is None:
                # return the empty set of permissions
                return DENY

            identity = User.by_id(self.user_id)

            # first, check if we're the project owner
            if doc.owner == identity:
                return WRITER

            acl = DBSession.query(ProjectACLEntry).filter(
                ProjectACLEntry.user == identity,
                ProjectACLEntry.project == doc.project
            ).first()

            if acl is None:
                return DENY

            return {
                ProjectACLEntry.READER: READER,
                ProjectACLEntry.WRITER: WRITER
            }.get(acl.level, DENY)

    return CerebroSessionAuthPolicy
