import faker
from django.test import TestCase
from ..models import Ingrediente, Receita, ReceitaIngrediente
from ..serializer import IngredienteSerializer, ReceitaSerializer, EntradaEstoqueSerializer, PerdaSerializer, ReceitaIngredienteSerializer
from decimal import Decimal

"""

A ideia desse arquivo é testar os serializadores criados no arquivo serializers.py

Os testes de serializadores, se baseiam em dois aspectos, testar a saídas dos dados dos serializadores, ou seja,
eles passaram os dados dos modelos para json, e a entrada dos dados, os dados virem em json, e serem convertidos para
o modelo.

"""

fake_data = faker.Faker()

class IngredienteSerializerTestCase(TestCase):
    def setUp(self):
        self.dados_validos = {
            'nome': 'Salmão',
            'unidade_medida': 'kg'
        }

    def test_ingrediente_serializer_success(self):
        # testando a serialização com dados válidos

        serializer = IngredienteSerializer(data=self.dados_validos)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        novo_ingrediente = serializer.save()
        self.assertEqual(novo_ingrediente.nome, 'Salmão')

    def test_ingrediente_serializer_fail(self):
        # testando a serialização com dados inválidos

        dados_invalidos = {
            'nome': 'Salmão',
            'unidade_medida': 'kgs'
        }

        serializer = IngredienteSerializer(data=dados_invalidos)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_ingrediente_serializer_output(self):
        # vou tentar pegar um objeto serializado para ver o que acontece

        serializer = IngredienteSerializer(data=self.dados_validos)

        serializer.is_valid()
        serializer.save()

        dados = serializer.data

        self.assertEqual(dados['nome'], 'Salmão')
        self.assertEqual(dados['unidade_medida'], 'kg')

class EntradaPerdaSerializerTestCase(TestCase):
    def setUp(self):
        self.ingrediente = Ingrediente.objects.create(
            nome='Arroz Japonês',
            unidade_medida='kg'
        )

    def test_entrada_estoque_input_output_success(self):
        # tentar verificar a criação de uma entrada e consultar essa entrada
        dados_validos = {
            'ingrediente': self.ingrediente.id,
            'quantidade': 0.3,
            'preco': 35.40,
            'validade': '2027-05-10',
        }

        serializer = EntradaEstoqueSerializer(data=dados_validos)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        entrada = serializer.data

        self.assertEqual(float(entrada['quantidade']), 0.3)
        self.assertEqual(entrada['ingrediente'], dados_validos['ingrediente'])
        self.assertEqual(entrada['ingrediente_nome'], self.ingrediente.nome)

    def test_entrada_estoque_input_ingrediente_inexistente(self):
        # A ideia aqui é tentar criar uma entrada para um ingrediente que não existe
        dados_validos = {
            'ingrediente': self.ingrediente.id + 1005,
            'quantidade': 0.3,
            'preco': 35.40,
            'validade': '2027-05-10',
        }

        serializer = EntradaEstoqueSerializer(data=dados_validos)

        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn('ingrediente', serializer.errors)

    def test_perda_input_output_success(self):
        # tentar criar registrar uma perda e depois obter as informações dessa perda com sucesso
        dados_validos = {
            'ingrediente': self.ingrediente.id,
            'motivo': 'Estragou',
            'quantidade': Decimal('0.08')
        }

        serializer = PerdaSerializer(data=dados_validos)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        perda = serializer.data
        self.assertEqual(perda['motivo'], 'Estragou')
        self.assertEqual(perda['ingrediente_nome'], 'Arroz Japonês')
        self.assertEqual(Decimal(perda['quantidade']), Decimal('0.08'))


class ReceitaSerializerTestCase(TestCase):
    def setUp(self):
        self.salmao = Ingrediente.objects.create(
            nome='Salmão',
            unidade_medida='kg'
        )
        self.arroz = Ingrediente.objects.create(
            nome='Arroz Japonês',
            unidade_medida='kg'
        )

        self.receita = Receita.objects.create(nome='Sashimi Salmão')

        self.item_receita = ReceitaIngrediente.objects.create(
            receita=self.receita,
            ingrediente=self.salmao,
            quantidade=Decimal('0.150')
        )

    def test_receita_output_success(self):
        # testando como os dados são enviados por json
        serializaer = ReceitaSerializer(instance=self.receita)
        dados_receita = serializaer.data

        self.assertIn('itens', dados_receita)
        self.assertIn('ingrediente_nome', dados_receita['itens'][0])
        self.assertEqual(dados_receita['itens'][0]['ingrediente_nome'], 'Salmão')

    def test_receita_input_success(self):
        # criar uma receita completa
        receita = {
            'nome': 'Sushi Filadélfia',
            'itens': [
                {'ingrediente': self.arroz.id, 'quantidade': '0.010'},
                {'ingrediente': self.salmao.id, 'quantidade': '0.030'}
            ]
        }

        serializer = ReceitaSerializer(data=receita)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        receita_completa = serializer.data

        self.assertIn('nome', receita_completa)
        self.assertEqual('Sushi Filadélfia', receita_completa['nome'])
        self.assertIn('itens', receita_completa)
        self.assertIn('ingrediente', receita_completa['itens'][0])
        self.assertIn('ingrediente_nome', receita_completa['itens'][1])
        self.assertEqual(receita_completa['itens'][0]['ingrediente_nome'], self.arroz.nome)
        self.assertEqual(receita_completa['itens'][1]['ingrediente_nome'], self.salmao.nome)
