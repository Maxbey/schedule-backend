from celery.result import AsyncResult
from django.http import HttpResponse
from django.core.cache import cache

from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework.response import Response

from ..models import Specialty, Troop, Discipline, Theme, Teacher, Audience, \
    ThemeType, Lesson

from .serializers import SpecialtySerializer, TroopSerializer, \
    DisciplineSerializer, ThemeSerializer, TeacherSerializer, \
    AudienceSerializer, ThemeTypeSerializer, BuildScheduleSerializer, \
    TeacherLoadStatisticsSerializer, TroopProgressStatisticsSerializer, \
    SpecialtyCourseLengthSerializer
from ..exporters import ExcelExporter

class AuthMixin(object):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [TokenAuthentication]


class BaseScheduleViewSet(AuthMixin, viewsets.ModelViewSet):
    pass


class SpecialtyViewSet(BaseScheduleViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['code']

    @detail_route(methods=['get'])
    def course_length(self, request, pk):
        specialty = self.get_object()

        serializer = SpecialtyCourseLengthSerializer(instance=specialty)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class ScheduleViewSet(AuthMixin, mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
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


class TeacherLoadStatisticsViewSet(AuthMixin, viewsets.GenericViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherLoadStatisticsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer_class = self.get_serializer_class()
        request_serializer = serializer_class(
            data=request.query_params, context=self.get_serializer_context()
        )
        request_serializer.is_valid(raise_exception=True)

        context = self.get_serializer_context()
        context.update(
            date_from=request_serializer.validated_data['date_from'],
            date_to=request_serializer.validated_data['date_to']
        )

        response_serializer = serializer_class(
            queryset, context=context, many=True
        )

        return Response(response_serializer.data)


class TroopProgressStatisticsViewSet(AuthMixin, mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     viewsets.GenericViewSet):
    queryset = Troop.objects.all()
    serializer_class = TroopProgressStatisticsSerializer

    paginator = None
