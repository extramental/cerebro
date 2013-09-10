from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid
from pyramid.interfaces import IAuthenticationPolicy

from zope.interface import implements

from .models import DBSession
from .models.auth import User

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from pyramid.security import Everyone, Authenticated, has_permission


class IdentifiedRequest(Request):
    @reify
    def identity(self):
        userid = unauthenticated_userid(self)

        if userid is None:
            return None

        try:
            return DBSession.query(Person).filter(Person.id == userid).one()
        except (NoResultFound, MultipleResultsFound):
            return None

    def has_permission(self, permission, context):
        return has_permission(permission, context, self)


class DBAuthenticationPolicy(object):
    implements(IAuthenticationPolicy)

    def unauthenticated_userid(self, request):
        return request.session.get("identity_id")

    def authenticated_userid(self, request):
        # this function is unnecessary... but we implement it out of
        # conformance
        userid = self.unauthenticated_userid(request)

        if userid is None:
            return userid

        try:
            return DBSession.query(User).filter(User.id == userid).one()
        except (NoResultFound, MultipleResultsFound):
            return None

    def remember(self, request, principal, **kwargs):
        request.session["identity_id"] = principal
        request.session.save()

    def forget(self, request):
        if "identity_id" in request.session:
            del request.session["identity_id"]
        request.session.save()

    def effective_principals(self, request):
        principals = [Everyone]

        if request.identity_id.is_anonymous:
            return principals

        principals.extend([
            Authenticated,
            "user_id:{}".format(request.identity.id)
        ])

        return principals
