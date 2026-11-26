from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import faker

# Create your tests here.

"""
25/11/26

Vou criar os testes para a classe RegisterUserView

Vou cobrir os seguintes cenários:

Sucesso ao criar usuário
CSRF token ausêncte
Email ausente
Email em uso
First_name ausênte
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

    def test_register_user_view_success(self):
        # vou testar a view de regsitrar usuários

        client_csrf = APIClient(enforce_csrf_checks=True)

        email_teste = fake_data.free_email()
        password = fake_data.password()

        novo_usuario = {
            'email': email_teste,
            'first_name': fake_data.first_name(),
            'last_name': fake_data.last_name(),
            'password': password,
            'confirm_password': password
        }

        csrf_resp = client_csrf.get(self.csrf_url)
        csrf_token = csrf_resp.data['csrf_token']

        response = client_csrf.post(
            reverse('accounts:register_user'), 
            novo_usuario,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_view_csrf_ausente(self):
        # vou tentar registar um usuário sem enviar o token csrf só para ver o que acontece.

        client_csrf = APIClient(enforce_csrf_checks=True)

        email_teste = fake_data.free_email()
        password = fake_data.password()

        novo_usuario = {
            'email': email_teste,
            'first_name': fake_data.first_name(),
            'last_name': fake_data.last_name(),
            'password': password,
            'confirm_password': password
        }

        response = client_csrf.post(
            reverse('accounts:register_user'),
            novo_usuario,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_view_email_ausente(self):
        # vou tentar registar um usuário sem enviar o email só para ver o que acontece.

        password = fake_data.password()

        novo_usuario = {
            'first_name': fake_data.first_name(),
            'last_name': fake_data.last_name(),
            'password': password,
            'confirm_password': password
        }

        response = self.client.post(
            reverse('accounts:register_user'),
            novo_usuario,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_view_email_repetido(self):
        # vou testar a view de regsitrar usuários, com um email já em uso

        password = fake_data.password()

        novo_usuario = {
            'email': email_primeiro,
            'first_name': fake_data.first_name(),
            'last_name': fake_data.last_name(),
            'password': password,
            'confirm_password': password
        }

        csrf_resp = self.client.get(self.csrf_url)
        csrf_token = csrf_resp.data['csrf_token']

        response = self.client.post(
            reverse('accounts:register_user'), 
            novo_usuario,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_view_first_name_ausente(self):
            # vou testar a view de regsitrar usuários sem pssar o primeiro nome
    
            client_csrf = APIClient(enforce_csrf_checks=True)
    
            email_teste = fake_data.free_email()
            password = fake_data.password()
    
            novo_usuario = {
                'email': email_teste,
                'last_name': fake_data.last_name(),
                'password': password,
                'confirm_password': password
            }
    
            csrf_resp = client_csrf.get(self.csrf_url)
            csrf_token = csrf_resp.data['csrf_token']
    
            response = client_csrf.post(
                reverse('accounts:register_user'), 
                novo_usuario,
                format='json',
                HTTP_X_CSRFTOKEN=csrf_token
            )
    
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)