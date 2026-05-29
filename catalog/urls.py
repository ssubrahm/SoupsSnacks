from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'cost-components', views.ProductCostComponentViewSet, basename='cost-component')

urlpatterns = [
    path('', include(router.urls)),
]
