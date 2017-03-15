from rest_framework import filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets

from ..models import Specialty, Troop, Discipline, Theme, Teacher, Audience, \
    ThemeType

from .serializers import SpecialtySerializer, TroopSerializer, \
    DisciplineSerializer, ThemeSerializer, TeacherSerializer, \
    AudienceSerializer, ThemeTypeSerializer


class BaseScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [TokenAuthentication]


class SpecialtyViewSet(BaseScheduleViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['code']


class TroopViewSet(BaseScheduleViewSet):
    queryset = Troop.objects.all()
    serializer_class = TroopSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['code']


class DisciplineViewSet(BaseScheduleViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'short_name']


class ThemeViewSet(BaseScheduleViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class TeacherViewSet(BaseScheduleViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class AudienceViewSet(BaseScheduleViewSet):
    queryset = Audience.objects.all()
    serializer_class = AudienceSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['location']


class ThemeTypeViewSet(BaseScheduleViewSet):
    queryset = ThemeType.objects.all()
    serializer_class = ThemeTypeSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
