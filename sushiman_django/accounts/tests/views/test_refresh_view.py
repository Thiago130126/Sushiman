from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import faker

# Create your tests here.

"""
23/11/26

Vou criar os testes para as classes RefreshView

Vou cobrir os seguintes cenários:

RefreshView
    falha 401 se a requisição não tiver o cookie refresh_token
    falha 401 se o cookie for inválido ou adulterado
    Sucesso (200) e renovação dos cookies quando o refresh_token for válido
"""

User = get_user_model()
fake_data = faker.Faker()

email_primeiro = fake_data.free_email()

class AccountsViewsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=email_primeiro,
            password=fake_data.password()
        )
        self.csrf_url = reverse('accounts:csrf_token')
        self.refresh_url = reverse('accounts:refresh_token')

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

        client_csrf = APIClient(enforce_csrf_checks=True)

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        refresh = RefreshToken.for_user(self.user)
        client_csrf.cookies['refresh_token'] = str(refresh)

        response = client_csrf.post(self.refresh_url, HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
