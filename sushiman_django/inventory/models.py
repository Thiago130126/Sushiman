from django.db import models

# Create your models here.

class Ingrediente(models.Model):
    class UnidadeMedida(models.TextChoices):
        GRAMA = 'g', 'Gramas'
        QUILO = 'kg', 'Quilos'
        MILILITRO = 'ml', 'Mililitros'
        LITROS = 'l', 'Litros'
        UNIDADE = 'un', 'Unidade'

    nome = models.CharField(max_length=150)
    unidade_medida = models.CharField(max_length=20, choices=UnidadeMedida.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'

    def __str__(self):
        return f'{self.nome}, ({self.unidade_medida})'

class Receita(models.Model):
    nome = models.CharField(max_length=150)
    ingredientes = models.ManyToManyField(
        Ingrediente,
        through='ReceitaIngrediente',
        related_name='receitas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'

class ReceitaIngrediente(models.Model):
    receita = models.ForeignKey(Receita, related_name='itens', on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['receita', 'ingrediente'],
                name='unique_receita_ingrediente'
            )
        ]

class EntradaEstoque(models.Model):
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.PROTECT,
        related_name='entradas'
    )
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    validade = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Entradas mais recentes primeiro por padrão
        indexes = [
            models.Index(fields=['validade'], name='idx_entrada_validade'),
            models.Index(fields=['-created_at'], name='idx_entrada_created_at'),
        ]
        verbose_name = 'Entrada de Estoque'
        verbose_name_plural = 'Entradas de Estoque'


    def __str__(self):
        return f'Entrada: {self.quantidade} {self.ingrediente.unidade_medida} de {self.ingrediente}'

class Perda(models.Model):
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.PROTECT,
        related_name='perdas'
    )
    motivo = models.CharField(max_length=200)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Perdas mais recentes primeiro
        indexes = [
            models.Index(fields=['-created_at'], name='idx_perda_created_at'),
        ]
        verbose_name = 'Perda de Estoque'
        verbose_name_plural = 'Perdas de Estoque'


    def __str__(self):
        return f'Perda: {self.quantidade} {self.ingrediente.unidade_medida} de {self.ingrediente}; motivo: {self.motivo}'
