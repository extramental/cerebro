from pyramid.response import Response
from pyramid.view import view_config


@view_config(context="cerebro.models.Root", renderer="home/index.mako")
def index(request):
    return {}

