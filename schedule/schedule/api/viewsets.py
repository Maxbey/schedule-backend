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


class TroopViewSet(BaseScheduleViewSet):
    queryset = Troop.objects.all()
    serializer_class = TroopSerializer


class DisciplineViewSet(BaseScheduleViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
