from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import notfound_view_config, view_config

@notfound_view_config(append_slash=True)
def notfound(request):
    return HTTPNotFound("HTTP not found")
