from decouple import config
from rest_framework_simplejwt.tokens import RefreshToken

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