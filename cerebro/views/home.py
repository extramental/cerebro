from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name="home_index", renderer="home/index.mako")
def index(request):
    return {}

