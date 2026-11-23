from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import faker

# Create your tests here.

"""
23/11/26

Vou criar os testes para as classes CsrfTokenView, RefreshView e CookieJWTAuthentication

Vou cobrir os seguintes cenários:

CsrfTokenView
    responde com status 200
    retorna a chave 'csrf_token' no json e o cookie csrftoken  na resposta

RefreshView
    falha 401 se a requisição não tiver o cookie refresh_token
    falha 401 se o cookie for inválido ou adulterado
    Sucesso (200) e renovação dos cookies quando o refresh_token for válido

CookieJWTAuthentication
    retorna 401 quando não há cookie
    bloqueia com falha csrf quando o cookie csrf estiver ausente ou inválido
    retorna 200 quando o cookie do token de acesso e o CSRF token estiverem presentes e válidos
"""

User = get_user_model()
fake_data = faker.Faker()

class AccountsViewsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=fake_data.free_email(),
            password=fake_data.password()
        )
        self.csrf_url = reverse('accounts:csrf_token')
        self.refresh_url = reverse('accounts:refresh_token')

    def test_get_csrf_token_success(self):
        # Garante que a url 'api/accounts:refresh' vai retornar o token no body e no cookie

        response = self.client.get(self.csrf_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrf_token', response.data)
        self.assertIn('csrftoken', response.cookies)

    def test_refresh_token_missing_cookie(self):
        # Deve retornar 401 se não houver o cookie 'refresh_token' na requisição

        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['erro'], 'Ausência de token')

    def test_refresh_token_invalid(self):
        # Deve retornar 401 se o refresh_token no cookie for inválido

        self.client.cookies['refresh_token'] = 'token_invalido_ou_expirado'
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['erro'], 'Token inválido')

    def test_refresh_token_success(self):
        # Deve renovar os cookies access_token e refresh_token

        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['refresh_token'] = str(refresh)

        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)