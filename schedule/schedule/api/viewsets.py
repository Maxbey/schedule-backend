from celery.result import AsyncResult
from django.http import HttpResponse
from django.core.cache import cache

from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework.response import Response

from ..models import Specialty, Troop, Discipline, Theme, Teacher, Audience, \
    ThemeType, Lesson

from .serializers import SpecialtySerializer, TroopSerializer, \
    DisciplineSerializer, ThemeSerializer, TeacherSerializer, \
    AudienceSerializer, ThemeTypeSerializer, BuildScheduleSerializer

from ..exporters import ExcelExporter


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


class ExportScheduleViewSet(viewsets.GenericViewSet):
    @list_route()
    def excel(self, request):
        ExcelExporter.export(Lesson.objects)

        with open('./exported.xlsx', "rb") as excel:
            data = excel.read()

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=schedule.xlsx'

        return response


class ScheduleViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [TokenAuthentication]

    serializer_class = BuildScheduleSerializer
    schedule_build_task = 'build_schedule'

    def list(self, request, **kwargs):
        if self.is_build_done():
            return Response({}, status.HTTP_200_OK)

        total_term_load = float(cache.get('total_term_load'))
        current_term_load = float(cache.get('current_term_load'))

        struct = {
            'status': 'BUILD_PROCESSING',
            'progress': current_term_load / total_term_load
        }

        return Response(struct, status.HTTP_400_BAD_REQUEST)

    def is_build_done(self):
        task_id = cache.get(self.schedule_build_task)

        if task_id:
            status = AsyncResult(task_id).status

            return status == 'SUCCESS'

        return True
