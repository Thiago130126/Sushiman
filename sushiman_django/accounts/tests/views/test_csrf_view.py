from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import faker

# Create your tests here.

"""
25/11/26

Vou criar os testes para as classes CsrfTokenView

Vou cobrir os seguintes cenários:

CsrfTokenView
    responde com status 200
    retorna a chave 'csrf_token' no json e o cookie csrftoken  na resposta
    
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

    def test_get_csrf_token_success(self):
        # Garante que a url 'api/accounts:refresh' vai retornar o token no body e no cookie

        response = self.client.get(self.csrf_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrf_token', response.data)
        self.assertIn('csrftoken', response.cookies)