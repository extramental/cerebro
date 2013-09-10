from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.path import AssetResolver

from pyramid_webassets import includeme as includeme_pyramid_webassets

from sqlalchemy import engine_from_config

from pyramid_beaker import session_factory_from_settings

from .auth import identity_for_request, request_has_permission, \
                  DBAuthenticationPolicy
from .models import DBSession, Base


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)

    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    config.add_request_method(identity_for_request, "identity", reify=True)
    config.add_request_method(request_has_permission, "has_permission")

    config.add_static_view("static", "static", cache_max_age=3600)
    config.scan()

    config.set_authentication_policy(DBAuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())

    # intercept pyramid_webassets settings
    config.registry.settings["webassets.base_dir"] = AssetResolver().resolve(config.registry.settings["webassets.base_dir"]).abspath()
    includeme_pyramid_webassets(config)

    route(config)

    return config.make_wsgi_app()


def route(config):
    config.add_route("home", "/")
