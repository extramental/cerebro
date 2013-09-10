from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name="project_index", renderer="project/index.mako",
             permission="read")
def index(request):
    return {"project": request.context}

