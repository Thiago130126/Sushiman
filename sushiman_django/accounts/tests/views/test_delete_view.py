from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import faker

"""
26/11/26

Vou criar os testes para a classe UserDeleteView

Vou cobrir os seguintes cenários:

Sucesso ao deletar conta - check
tentar excluir sem refresh_token - check
tentar excluir com token inválido - check
tentar excluir sem csrf token - check

"""

fake_data = faker.Faker()
client_csrf = APIClient(enforce_csrf_checks=True)

User = get_user_model()

email_usado = fake_data.free_email()
senha_usada = fake_data.password()
nome_usado = fake_data.first_name()
last_name_usado = fake_data.last_name()

class UserDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=email_usado,
            password=senha_usada,
            first_name=nome_usado,
            last_name=last_name_usado
        )

        self.csrf_url = reverse("accounts:csrf_token")
        self.refresh_url = reverse("accounts:refresh_token")

    def test_user_delete_view_success(self):
        # testar se a view deleta usuário com sucesso

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados_login = {
            'email': email_usado,
            'password': senha_usada
        }

        client_csrf.post(
            reverse("accounts:login_user"),
            data=dados_login,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        response = client_csrf.delete(
            reverse("accounts:delete_user"),
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_delete_view_sem_refresh_token(self):
        # tentarei deletar a conta sem o token de refresh

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados_login = {
            'email': email_usado,
            'password': senha_usada
        }

        client_csrf.post(
            reverse('accounts:login_user'),
            data=dados_login,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        client_csrf.cookies.pop('refresh_token', None)

        response = client_csrf.delete(
            reverse("accounts:delete_user"),
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_delete_view_refresh_token_invalido(self):
        # tentarei deletar a conta sem o token de refresh

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados_login = {
            'email': email_usado,
            'password': senha_usada
        }

        client_csrf.post(
            reverse('accounts:login_user'),
            data=dados_login,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        token_str = client_csrf.cookies['refresh_token'].value
        RefreshToken(token_str).blacklist()

        response = client_csrf.delete(
            reverse("accounts:delete_user"),
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_delete_view_sem_csrf_token(self):
        # tentarei deletar a conta sem o token de refresh

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados_login = {
            'email': email_usado,
            'password': senha_usada
        }

        client_csrf.post(
            reverse('accounts:login_user'),
            data=dados_login,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        response = client_csrf.delete(
            reverse("accounts:delete_user"),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)