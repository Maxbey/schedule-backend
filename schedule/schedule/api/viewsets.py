from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets

from ..models import Specialty, Troop

from .serializers import SpecialtySerializer, TroopSerializer


class BaseScheduleViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [TokenAuthentication]


class SpecialtyViewset(BaseScheduleViewset):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer


class TroopViewset(BaseScheduleViewset):
    queryset = Troop.objects.all()
    serializer_class = TroopSerializer
