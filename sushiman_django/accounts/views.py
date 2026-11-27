from django.shortcuts import get_object_or_404
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from rest_framework_simplejwt.exceptions import TokenError
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializer import UserRegisterSerializer, CustomUserSerializer
from rest_framework.generics import CreateAPIView
from .authentication import CSRFRequired, CookieJWTAuthentication
from django.contrib.auth import authenticate
from .utils import set_auth_cookies, delete_cookies


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

    def create(self, request, *args, **kwargs):
        seralizer = self.get_serializer(data=request.data)
        seralizer.is_valid(raise_exception=True)
        user = seralizer.save()

        headers = self.get_success_headers(seralizer.data)
        response = Response(
            {'message': 'Conta criada com sucesso'},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

        logger.info("Cadastro realizado com sucesso. ID: %s", user.id)
        return set_auth_cookies(response, user)

class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny, CSRFRequired]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            logger.warning("Tentativa de login sem email ou senha fornecidos")
            return Response(
                {'detail': 'E-mail e senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)
        if not user:
            logger.warning("Falha de autenticação para o email: %s", email)
            return Response(
                {'erro': 'Email ou senha incorretos'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response({'message': 'Login realizado com sucesso'}, status=status.HTTP_200_OK)

        response = set_auth_cookies(response, user)

        logger.info("Sucesso para logar o usuário ID: %s", user.id)

        return response


class UserProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = CustomUserSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid()
        serializer.save()

        logger.info("Usuário atualizado com sucesso; ID: %s", request.user.id)
        return Response({'message': 'Usuário atualizado com sucesso'}, status=status.HTTP_200_OK)

class UserLogoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        cookies_names = ['access_token', 'refresh_token']

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                logger.warning("Tentativa de deslogar usando um token inválido, ID: %s", request.user.id)
                return Response({'erro': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            logger.info("Logout realizado sem refresh_token no cookie. ID: %s", request.user.id)

        response = Response({'message': 'Logout realizado com sucesso'}, status=status.HTTP_200_OK)

        response = delete_cookies(response, cookies_names)

        logger.info("Usuario deslogado com sucesso; ID: %s", request.user.id)
        return response

class UserDeleteView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                user = request.user
                user_id = user.id
                token = RefreshToken(refresh_token)
                token.blacklist()
                user.delete()
            except TokenError:
                logger.warning("Tentativa de deletar conta usando um token inválido, ID: %s", request.user.id)
                return Response({'erro': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            logger.warning("Tentativa de deletar conta sem refresh_token, ID: %s", request.user.id)
            return Response({'erro': 'Refresh token ausêncte'}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({'message': 'Conta deletada com sucesso'}, status=status.HTTP_200_OK)

        response = delete_cookies(response)

        logger.info("Usuario deletado com sucesso; ID: %s", user_id)
        return response
