from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from .viewsets import SpecialtyViewSet, TroopViewSet, DisciplineViewSet, \
    ThemeViewSet, TeacherViewSet, AudienceViewSet, ThemeTypeViewSet, \
    ExportScheduleViewSet, ScheduleViewSet

router = SimpleRouter()

router.register(r'specialty', SpecialtyViewSet)
router.register(r'troop', TroopViewSet)
router.register(r'discipline', DisciplineViewSet)
router.register(r'theme', ThemeViewSet)
router.register(r'theme_type', ThemeTypeViewSet)
router.register(r'teacher', TeacherViewSet)
router.register(r'audience', AudienceViewSet)
router.register(r'export', ExportScheduleViewSet, base_name='export')
router.register(
    r'schedule',
    ScheduleViewSet,
    base_name='schedule_operations'
)

urlpatterns = [
    url(r'^v1/', include(router.urls, namespace='schedule-v1')),
]

