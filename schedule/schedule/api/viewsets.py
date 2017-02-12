from rest_framework import filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets

from ..models import Specialty, Troop, Discipline

from .serializers import SpecialtySerializer, TroopSerializer, \
    DisciplineSerializer


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
