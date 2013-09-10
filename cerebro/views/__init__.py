from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='home', renderer='_layout.mako')
def my_view(request):
    return {}

