from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)

    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    config.add_static_view("static", "static", cache_max_age=3600)
    config.scan()

    route(config)

    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    return config.make_wsgi_app()


def route(config):
    config.add_route("home", "/")
