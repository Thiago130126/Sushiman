from rest_framework import serializers
from .models import Ingrediente, Receita, ReceitaIngrediente, EntradaEstoque, Perda
from django.db import transaction

class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = ['id', 'nome', 'unidade_medida',]

class ReceitaIngredienteSerializer(serializers.ModelSerializer):
    ingrediente_nome = serializers.ReadOnlyField(source='ingrediente.nome')
    unidade_medida = serializers.ReadOnlyField(source='ingrediente.unidade_medida')

    class Meta:
        model = ReceitaIngrediente
        fields = ['id', 'receita', 'ingrediente', 'ingrediente_nome', 'unidade_medida', 'quantidade']
        read_only_fields = ['receita']

class ReceitaSerializer(serializers.ModelSerializer):
    itens = ReceitaIngredienteSerializer(many=True)

    class Meta:
        model = Receita
        fields = ['id', 'nome', 'itens']

    def create(self, validated_data):
        itens_data = validated_data.pop('itens')

        with transaction.atomic():
            receita = Receita.objects.create(**validated_data)

            for item_data in itens_data:
                ReceitaIngrediente.objects.create(receita=receita, **item_data)

        return receita

class EntradaEstoqueSerializer(serializers.ModelSerializer):
    ingrediente_nome = serializers.ReadOnlyField(source='ingrediente.nome')
    unidade_medida = serializers.ReadOnlyField(source='ingrediente.unidade_medida')

    class Meta:
        model = EntradaEstoque
        fields = ['id', 'ingrediente', 'ingrediente_nome', 'unidade_medida', 'quantidade', 'preco', 'validade', 'created_at']

class PerdaSerializer(serializers.ModelSerializer):
    ingrediente_nome = serializers.ReadOnlyField(source='ingrediente.nome')
    unidade_medida = serializers.ReadOnlyField(source='ingrediente.unidade_medida')

    class Meta:
        model = Perda
        fields = ['id', 'ingrediente', 'ingrediente_nome', 'unidade_medida', 'motivo', 'quantidade', 'created_at']