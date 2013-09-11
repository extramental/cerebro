from pyramid.response import Response
from pyramid.view import view_config


@view_config(context="cerebro.models.project.Project", renderer="project/index.mako",
             permission="read")
def index(request):
    return {}

