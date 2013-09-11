from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.security import forget

from ..models import Root


@view_config(context=Root, renderer="home/index.mako")
def index(request):
    return {}


@view_config(context=Root, name="logout", request_method="POST")
def logout(request):
    headers = forget(request)
    return HTTPFound(request.referrer or request.resource_url(request.root),
                     headers)
