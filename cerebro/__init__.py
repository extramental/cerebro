from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from webassets import Bundle

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
    config.add_static_view("static", "static", cache_max_age=3600)
    config.scan()

    route(config)

    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    return config.make_wsgi_app()


def route(config):
    config.add_route("home", "/")
