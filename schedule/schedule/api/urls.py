from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from .viewsets import SpecialtyViewSet, TroopViewSet, DisciplineViewSet

router = SimpleRouter()

router.register(r'specialty', SpecialtyViewSet)
router.register(r'troop', TroopViewSet)
router.register(r'discipline', DisciplineViewSet)

urlpatterns = [
    url(r'^v1/', include(router.urls, namespace='schedule-v1')),
]

