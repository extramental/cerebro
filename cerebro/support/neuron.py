from sqlalchemy import engine_from_config

from pyramid.paster import bootstrap
from pyramid.request import Request
from pyramid_beaker import session_factory_from_settings

from beaker.session import Session
from cerebro.models import DBSession, Base

from cerebro.models.auth import User
from cerebro.models.project import Project, Doc

from tornado.options import define, options

define("cerebro_config", help="cerebro config file to use")


class CerebroAuthPolicy(object):
    """
    An auth policy for Neuron. This code does not get called inside the Cerebro
    application -- instead, Neuron runs this code to perform auth.
    """
    def __init__(self, application):
        env = bootstrap(options.cerebro_config)
        settings = env["registry"].settings

        engine = engine_from_config(settings, "sqlalchemy.")
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

        self.session_factory = session_factory_from_settings(settings)

    def authenticate(self, request):
        # TODO: yeah.
        return 1

        session = self.session_factory(Request({
            "HTTP_COOKIE": str(request.cookies)
        }))

        user = User.by_id(session.get("user_id", None))

        if user is None:
            return None

        return user.id

    def authorize(self, doc_id):
        return True
        doc = Doc.by_id(doc_id)

        if doc is None:
            return False

        # TODO: yeah.
        return True
