from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import faker


"""
26/11/26

Vou criar os testes para a classe UserLoginView

Vou cobrir os seguintes cenários:

Sucesso ao logar usuario - check
CSRF token ausênte - check
Email ausente - check
senha ou email incorreta - check
verificar existência do token - check
usuario não encontrado - check
"""

User = get_user_model()
fake_data = faker.Faker()

email_primeiro = fake_data.free_email()
senha_primeiro = fake_data.password()

client_csrf = APIClient(enforce_csrf_checks=True)

class LoginViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=email_primeiro,
            password=senha_primeiro,
            first_name='João',
            last_name='Pereira',
        )

        self.csrf_url = reverse("accounts:csrf_token")
        self.refresh_url = reverse("accounts:refresh_token")

    def test_login_user_view_success(self):
        # aqui vou primeiramente testar o login realizado com sucesso

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados = {
            'email': email_primeiro,
            'password': senha_primeiro
        }

        response = client_csrf.post(
            reverse("accounts:login_user"),
            data=dados,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_view_csrf_ausente(self):
        # vou testar fazer o login sem o csrf token

        dados = {
            'email': email_primeiro,
            'password': senha_primeiro
        }

        response = client_csrf.post(
            reverse("accounts:login_user"),
            data=dados,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_user_view_tokens_success(self):
        # vou verificar se os tokens estão sendo gerados e se estão presentes nos cookies

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        dados = {
            'email': email_primeiro,
            'password': senha_primeiro
        }

        response = client_csrf.post(
            reverse("accounts:login_user"),
            data=dados,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )


        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

        refresh_token = RefreshToken(response.cookies['refresh_token'].value)
        self.assertEqual(int(refresh_token['user_id']), self.user.id)

        access_token = AccessToken(response.cookies['access_token'].value)
        self.assertEqual(int(access_token['user_id']), self.user.id)

    def test_login_user_view_email_ausente(self):
        # testar o login mas sem mandar email

        dados = {
            'password': senha_primeiro
        }

        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        response = client_csrf.post(
            reverse("accounts:login_user"),
            data=dados,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_view_dados_incorretos(self):
        # email ou senha incorretos

        dados = {
            'email': email_primeiro,
            'password': fake_data.password()
        }

        response = self.client.post(
            reverse("accounts:login_user"),
            data=dados,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_user_view_usuario_nao_encontrado(self):
        # vou tentar logar com email e senha não cadastrados

        dados = {
            'email': fake_data.free_email(),
            'password': fake_data.password()
        }

        response = self.client.post(
            reverse('accounts:login_user'),
            data=dados,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
