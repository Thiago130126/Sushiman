from decouple import config
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import logging
from rest_framework import status

logger = logging.getLogger(__name__)

def set_auth_cookies(response, user):
    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)
    cookie_secure = config('COOKIE_SECURE', default=False, cast=bool)

    cookies = {
        'access_token': access_token,
        'refresh_token': str(refresh_token)
    }

    for cookie, token in cookies.items():
        response.set_cookie(
            key=cookie,
            value=token,
            httponly=True,
            secure=cookie_secure,
            samesite='Lax'
        )

    return response

def delete_cookies(response, cookies_names=None):

    if cookies_names is None:
        cookies_names = ['access_token', 'refresh_token']
    
    for cookie in cookies_names:
        response.delete_cookie(cookie)

    return response