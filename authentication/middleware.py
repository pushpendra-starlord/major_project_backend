from django.db import close_old_connections
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async
from jwt import decode as jwt_token_decode
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.auth import UserLazyObject, get_user
from channels.sessions import CookieMiddleware, SessionMiddleware

@database_sync_to_async
def get_jwttoken_user(user_token):
    """
    Return the user model instance associated with the given JWT Token.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    user = None
    if user_token:
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(user_token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            pass
        else:
            # token is valid, decode it
            jwt_decoded_data = jwt_token_decode(user_token, settings.SECRET_KEY)
            # Get the user ID
            user_id = jwt_decoded_data["user_id"]
            user = get_user_model().objects.get(id=user_id)
    return user or AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Middleware which populates scope["user"] from a JWT Token in Django Authorization Header.
    """

    def populate_scope(self, scope):
        # Make sure we have a session
        if "session" not in scope:
            raise ValueError(
                "TokenAuthMiddleware cannot find session in scope. "
                "SessionMiddleware must be above it."
            )
        # Make sure we have a query_string
        if "query_string" not in scope:
            raise ValueError(
                "TokenAuthMiddleware cannot find query_string in scope. "
            )
        # Add it to the scope if it's not there already
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    async def resolve_scope(self, scope):
        if "query_string" not in scope:
            raise ValueError(
                "TokenAuthMiddleware cannot find query_string in scope. "
            )
        user_token = parse_qs(scope["query_string"].decode("utf8")).get("user_token", [None])[0]
        if user_token:
            scope["user"]._wrapped = await get_jwttoken_user(user_token)
        else:
            scope["user"]._wrapped = await get_user(scope)

# Handy shortcut for applying all three layers at once
def TokenAuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(TokenAuthMiddleware(inner)))