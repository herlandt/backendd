# auditoria/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BitacoraViewSet

router = DefaultRouter()
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')

urlpatterns = [
    path('', include(router.urls)),
]