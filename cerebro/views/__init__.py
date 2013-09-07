from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='home', renderer='_layout.html')
def my_view(request):
    return {'project': 'cerebro'}
