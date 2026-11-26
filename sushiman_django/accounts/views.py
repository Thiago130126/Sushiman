from django.shortcuts import get_object_or_404
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from rest_framework_simplejwt.exceptions import TokenError
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializer import UserRegisterSerializer
from rest_framework.generics import CreateAPIView
from .authentication import CSRFRequired, CookieJWTAuthentication


logger = logging.getLogger(__name__)
# Create your views here.

refresh_path = 'accounts/api/refresh'
User = get_user_model()

# Eu chamei o cookie, que contém o token de acesso, de access_token

class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny, CSRFRequired]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            logger.warning('Tentativa de renovação de tokens sem o cookie de refresh')
            return Response({'erro': 'Ausência de token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            user_id = token['user_id']
            user = get_object_or_404(User, id=user_id)
            new_refresh_token = RefreshToken.for_user(user)
            new_access_token = str(new_refresh_token.access_token)
            token.blacklist()

            response = Response({'message': 'Access token, renovado com sucesso'})

            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=config('COOKIE_SECURE', default=False, cast=bool), # Trocar para True em produção
                samesite='Lax'
            )

            response.set_cookie(
                key='refresh_token',
                value=new_refresh_token,
                httponly=True,
                secure=config('COOKIE_SECURE', default=False, cast=bool), # Trocar para True em produção
                samesite='Lax'
            )

            logger.info('Renovação dos tokens de acesso realizada com sucesso para user_id=%s', user_id)
            return response

        except TokenError:
            logger.warning('Tentativa de refresh com token inválido ou expirado. IP: %s', request.META.get('REMOTE_ADDR'))
            return Response({'erro': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        csrf_token = get_token(request)
        return Response({
            'csrf_token': csrf_token
        })

class RegisterUserView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny, CSRFRequired]
    queryset = User.objects.all()