from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyOfferingViewSet

router = DefaultRouter()
router.register(r'daily-offerings', DailyOfferingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
