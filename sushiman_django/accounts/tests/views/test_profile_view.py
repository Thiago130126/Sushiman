from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import faker

"""
26/11/26

Vou criar os testes para a classe UserProfileView

Vou cobrir os seguintes cenários para o método get:

Sucesso ao visualizaer perfil - check
verificar as informações exibidas - check
bloquear usuário não logado - check

Para o método patch:

sucesso ao atualizar suas informações - check
verificar informações atualizadas - check
falhar ao tentar atualizar o email
"""

User = get_user_model()
client_csrf = APIClient(enforce_csrf_checks=True)
fake_data = faker.Faker()

email_usado = fake_data.free_email()
senha_usada = fake_data.password()
nome_usado = fake_data.first_name_female()
sobrenome_usado = fake_data.last_name()
data_nascimento_usada = fake_data.date_of_birth()

class UserProfileViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=email_usado,
            password=senha_usada,
            first_name=nome_usado,
            last_name=sobrenome_usado,
            data_nascimento=data_nascimento_usada
        )

        self.csrf_url = reverse("accounts:csrf_token")
        self.refresh_url = reverse("accounts:refresh_token")

    # ----- Método Get -----------

    def test_user_profile_success(self):
        # view funcionando perfeitamente
        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados = {
            'email': email_usado,
            'password': senha_usada
        }

        client_csrf.post(
            reverse("accounts:login_user"),
            data=dados,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )


        response = client_csrf.get(
            reverse("accounts:profile_user"),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile_content_response(self):
        # uma verificação das informações passadas para o frontend
        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados = {
            'email': email_usado,
            'password': senha_usada
        }

        client_csrf.post(
            reverse("accounts:login_user"),
            data=dados,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        response = client_csrf.get(reverse("accounts:profile_user"))

        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('data_nascimento', response.data)
        self.assertNotIn('password', response.data)
        self.assertIn('id', response.data)

    def test_user_profile_usuario_nao_logado(self):
        # vou testar se o sistema impede o acesso de usuários não logados

        response = self.client.get(reverse("accounts:profile_user"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------- Patch ---------

    def test_user_profile_view_patch_success(self):
        # testar se dá tudo certo ao mudar as informações de um usuário

        dados_logar = {
            'email': email_usado,
            'password': senha_usada
        }

        dados_atualizar = {
            'first_name': 'João'
        }

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        client_csrf.post(
            reverse("accounts:login_user"),
            data=dados_logar,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        response = client_csrf.patch(
            reverse("accounts:profile_user"),
            data=dados_atualizar,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile_view_patch_check_information(self):
        # verificar as novas informações do usuário

        dados_logar = {
            'email': email_usado,
            'password': senha_usada
        }

        dados_atualizar = {
            'first_name': 'João'
        }

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        client_csrf.post(
            reverse("accounts:login_user"),
            data=dados_logar,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        client_csrf.patch(
            reverse("accounts:profile_user"),
            data=dados_atualizar,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        user = client_csrf.get(reverse("accounts:profile_user"))

        self.assertEqual(user.data['first_name'], 'João')
        self.assertNotEqual(user.data['first_name'], nome_usado)

    def test_user_profile_view_patch_email_fail(self):
        # testar se dá tudo certo ao mudar as informações de um usuário

        dados_logar = {
            'email': email_usado,
            'password': senha_usada
        }

        dados_atualizar = {
            'email': fake_data.free_email()
        }

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        client_csrf.post(
            reverse("accounts:login_user"),
            data=dados_logar,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        response = client_csrf.patch(
            reverse("accounts:profile_user"),
            data=dados_atualizar,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        user = client_csrf.get(reverse("accounts:profile_user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.data['email'], email_usado)