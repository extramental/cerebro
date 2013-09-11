from pyramid.response import Response
from pyramid.view import view_config


from ..models.project import Project


@view_config(context=Project, renderer="project/index.mako", permission="read")
def index(request):
    return {}

