from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from .viewsets import SpecialtyViewset, TroopViewset

router = SimpleRouter()

router.register(r'specialty', SpecialtyViewset)
router.register(r'troop', TroopViewset)

urlpatterns = [
    url(r'^v1/', include(router.urls, namespace='schedule-v1')),
]

