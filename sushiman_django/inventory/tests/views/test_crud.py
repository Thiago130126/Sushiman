from rest_framework.test import APIClient, APITestCase
import faker
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from ...models import Ingrediente

User = get_user_model()
fake_data = faker.Faker()
client_csrf = APIClient(enforce_csrf_checks=True)

email_admin = fake_data.free_email()
password_admin = fake_data.password()
name_admin = fake_data.first_name_female()
last_name_admin = fake_data.last_name()

email_user = fake_data.free_email()
password_user = fake_data.password()
name_user = fake_data.first_name_female()
last_name_user = fake_data.last_name()

dados_login_admin = {
    'email': email_admin,
    'password': password_admin
}


class CRUDViewsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email=email_admin,
            password=password_admin,
            first_name=name_admin,
            last_name=last_name_admin
        )

        self.user = User.objects.create_user(
            email=email_user,
            password=password_user,
            first_name=name_user,
            last_name=last_name_user
        )

        self.arroz = Ingrediente.objects.create(
            nome='Arroz Japonês',
            unidade_medida='kg'
        )

        self.atum = Ingrediente.objects.create(
            nome='Atum',
            unidade_medida='kg'
        )

        self.csrf_url = reverse("accounts:csrf_token")
        self.refresh_url = reverse("accounts:refresh_token")

    def csrf_token_request(self):
        # método auxiliar para pegar o csrf token
        #  
        csrf_request = client_csrf.get(self.csrf_url)
        csrf_token = csrf_request.data['csrf_token']

        return csrf_token

    def authenticate(self, data):
        # método utilitário para autenticar o usuário

        csrf_token = self.csrf_token_request()

        client_csrf.post(
            reverse("accounts:login_user"),
            data=data,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        return client_csrf

    def test_get_admin_success(self):
        # testando uma rota get do crud de ingrediente logado como admin

        rotas_a_testar = ['ingredientes-list', 'receitas-list', 'entradas-list', 'perdas-list']

        for rota_a_testar in rotas_a_testar:
            client = self.authenticate(dados_login_admin)

            response = client.get(
                reverse(f"inventory:{rota_a_testar}")
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_fail(self):
        # vou tentar acessar a rota GET do crudo ingrediente sem ser admin

        rotas_a_testar = ['ingredientes-list', 'receitas-list', 'entradas-list', 'perdas-list']

        for rota_a_testar in rotas_a_testar:

            dados_login = {
                'email': email_user,
                'password': password_user
            }

            client = self.authenticate(dados_login)

            response = client.get(reverse(f"inventory:{rota_a_testar}"))

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nao_logado_fail(self):
        # vou tentar acessar os objetos de cada crud sem estar logado

        rotas_a_testar = ['ingredientes-list', 'receitas-list', 'entradas-list', 'perdas-list']

        for rota in rotas_a_testar:

            response = client_csrf.get(reverse(f"inventory:{rota}"))

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_ingrediente_success(self):
        # vou testar se o serializador do ingrediente funciona de ponta a ponta por HTTP

        ingrediente_data = {
            'nome': 'Salmão',
            'unidade_medida': 'kg'
        }

        client = self.authenticate(dados_login_admin)
        csrf_token = self.csrf_token_request()

        response = client.post(
            reverse("inventory:ingredientes-list"),
            data=ingrediente_data,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn("Salmão", response.data['nome'])

    def test_post_entrada_perda_success(self):
        # vou testar os serializadores de entradas e perdas pela rota post

        perda_data = {
            'ingrediente': self.arroz.id,
            'motivo': 'Extraviou',
            'quantidade': '0.5'
        }

        entrada_data = {
            'ingrediente': self.arroz.id,
            'quantidade': '6.50',
            'preco': '70.90',
            'validade': '2027-06-13'
        }

        rotas = ['entradas-list', 'perdas-list']
        objetos = [entrada_data, perda_data]


        for rota, objeto in zip(rotas, objetos):
            csrf_token = self.csrf_token_request()
            client = self.authenticate(dados_login_admin)

            response = client.post(
                reverse(f"inventory:{rota}"),
                data=objeto,
                format='json',
                HTTP_X_CSRFTOKEN=csrf_token
            )

            data = response.data

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn('id', data)

    def test_receita_serializer_post_success(self):
        # vou testar o serializer de receita via HTTP post

        receita = {
            'nome': 'Sushi Atum',
            'itens': [
                {'ingrediente': self.arroz.id, 'quantidade': '0.10'},
                {'ingrediente': self.atum.id, 'quantidade': '0.25'}
            ]
        }

        csrf_token = self.csrf_token_request()
        client = self.authenticate(dados_login_admin)

        response = client.post(
            reverse("inventory:receitas-list"),
            data=receita,
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data

        self.assertIn("id", data)
        self.assertIn("Sushi Atum", data['nome'])
        self.assertIn("Atum", data["itens"][1]["ingrediente_nome"])