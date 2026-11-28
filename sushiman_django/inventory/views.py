from rest_framework.viewsets import ModelViewSet
from accounts.authentication import CookieJWTAuthentication
from rest_framework.permissions import IsAdminUser
from . import models
from . import serializer

# Create your views here.

# Sim, essas 5 linhas são o CRUD completo da tabela ingredientes, 2 rotas GET, POST, PUT, PATCH, DELETE
class IngredienteCRUDView(ModelViewSet):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = models.Ingrediente.objects.all()
    serializer_class = serializer.IngredienteSerializer

class EntradaEstoqueCRUDView(ModelViewSet):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = serializer.EntradaEstoqueSerializer
    queryset = models.EntradaEstoque.objects.all()

class PerdaCRUDView(ModelViewSet):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = serializer.PerdaSerializer
    queryset = models.Perda.objects.all()

class ReceitaCRUDView(ModelViewSet):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = serializer.ReceitaSerializer
    queryset = models.Receita.objects.all()

# sim, o CRUD das 4 tabelas está escrito entre as linhas 10 e 32
# cada CRUD tem 5 linhas, 20 linhas para fazer os 4.
# Eu ainda to de cara com isso