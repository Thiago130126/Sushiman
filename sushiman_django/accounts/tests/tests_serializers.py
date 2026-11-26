import faker
from ..serializer import UserRegisterSerializer, ProfileSerializer, CustomUserSerializer
from ..models import Profile
from django.contrib.auth import get_user_model
from django.test import TestCase

"""

A ideia desse arquivo é testar os serializadores criados no arquivo serializers.py

Os testes de serializadores, se baseiam em dois aspectos, testar a saídas dos dados dos serializadores, ou seja,
eles passaram os dados dos modelos para json, e a entrada dos dados, os dados virem em json, e serem convertidos para
o modelo.

"""

User = get_user_model()

fake_data = faker.Faker()

class SerializerTestsCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='novo@sushiman.com',
            password=fake_data.password(),
            first_name='João',
            last_name=fake_data.last_name(),
            data_nascimento=fake_data.date_of_birth(minimum_age=18, maximum_age=40)
        )
        self.profile = self.user.profile
        self.profile.bio = 'AdoroSushi'
        self.profile.email_publico = 'outro@sushiman.com'

    # testes de input

    def test_user_register_serializer_success_input(self):
        dados_registros = {
            'email': 'outro_novo@sushiman.com',
            'first_name': fake_data.first_name(),
            'last_name': fake_data.last_name(),
            'data_nascimento': '1995-05-10',
            'password': 'SenhaForte456!',
            'confirm_password': 'SenhaForte456!'
        }

        serializer = UserRegisterSerializer(data=dados_registros)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        novo_usuario = serializer.save()
        self.assertEqual(novo_usuario.email, 'outro_novo@sushiman.com')
        self.assertTrue(novo_usuario.check_password('SenhaForte456!') )

    def test_user_register_serializer_passwords_mismatch_input(self):
        dados_invalidos = {
            'email': 'outro@sushiman.com',
            'first_name': 'Pedro',
            'last_name': 'Souza',
            'password': 'SenhaUm123!',
            'confirm_password': 'SenhaDiferente456!'
        }
        serializer = UserRegisterSerializer(data=dados_invalidos)
        self.assertFalse(serializer.is_valid())
        self.assertIn('confirm_password', serializer.errors)

    
    
    def test_user_register_serializer_email_duplicado(self):
        # teste para a tentativa de registrar um usuário com um email já em uso

        dados_invalidos = {
            'email': 'novo@sushiman.com',
            'first_name': 'Pedro',
            'last_name': 'Souza',
            'password': 'SenhaUm123!',
            'confirm_password': 'SenhaUm123!'
        }

        serializer = UserRegisterSerializer(data=dados_invalidos)
        self.assertFalse(serializer.is_valid())

    def test_user_register_serializer_empty_field(self):
        # teste para ver se dá erro ao tentar cadastrar usuário sem nome

        dados_invalidos = {
            'email': 'novo@sushiman.com',
            'last_name': 'Souza',
            'password': 'SenhaUm123!',
            'confirm_password': 'SenhaUm123!'
        }

        serializer = UserRegisterSerializer(data=dados_invalidos)
        self.assertFalse(serializer.is_valid())

    # testes de saída (output)

    def test_user_serializer_output(self):
        serializer = CustomUserSerializer(instance=self.user)
        dados = serializer.data

        self.assertEqual(dados['email'], 'novo@sushiman.com')
        self.assertEqual(dados['first_name'], 'João')

        self.assertNotIn('password', dados)

    def test_profile_serializer_output(self):
        serializer = ProfileSerializer(instance=self.profile)
        dados = serializer.data

        print('CHAVES nos DADOS: ', dados.keys())

        self.assertEqual(dados['bio'], 'AdoroSushi')
        self.assertEqual(dados['email_publico'], 'outro@sushiman.com')
        self.assertNotIn('id', dados)