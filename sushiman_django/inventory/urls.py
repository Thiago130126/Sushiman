from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'inventory'

router = DefaultRouter()
router.register(r'ingredientes', views.IngredienteCRUDView, basename='ingredientes')
router.register(r'receitas', views.ReceitaCRUDView, basename='receitas')
router.register(r'entradas', views.EntradaEstoqueCRUDView, basename='entradas')
router.register(r'perdas', views.PerdaCRUDView, basename='perdas')

urlpatterns = [
    path('', include(router.urls))
]