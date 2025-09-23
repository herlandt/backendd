from rest_framework.routers import DefaultRouter
from .views import ResidenteViewSet

router = DefaultRouter()
router.register(r'residentes', ResidenteViewSet)

urlpatterns = router.urls