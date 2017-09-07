from django.core.cache import cache
from django.conf import settings

from rest_framework import serializers

from ..tasks import build_schedule
from ..models import Specialty, Troop, Discipline, Theme, Teacher, Audience, \
    ThemeType, Lesson


class TroopSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    day = serializers.ChoiceField(Troop.DAY_CHOICES)
    term = serializers.IntegerField()

    specialty = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects
    )
    specialty_code = serializers.CharField(
        read_only=True, source='specialty.code'
    )

    class Meta:
        model = Troop
        exclude = [
            'created_at',
            'updated_at'
        ]


class SpecialtySerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    troops = TroopSerializer(read_only=True, many=True)
    disciplines = serializers.PrimaryKeyRelatedField(
        read_only=True, source='related_disciplines_ids'
    )

    class Meta:
        model = Specialty
        exclude = [
            'created_at',
            'updated_at'
        ]


class SpecialtyCourseLengthSerializer(serializers.Serializer):
    course_length = serializers.SerializerMethodField()

    def get_course_length(self, specialty):
        struct = []

        for discipline in specialty.disciplines:
            discipline_struct = {
                'discipline': discipline.full_name,
                'terms': []
            }

            for term in xrange(1, settings.TERMS_COUNT + 1):
                durations = discipline.get_courses_length(term, specialty)
                if durations == (0, 0):
                    continue

                discipline_struct['terms'].append({
                    'term': term,
                    'lessons': durations[0],
                    'self_education': durations[1]
                })

            struct.append(discipline_struct)

        return struct


class ThemeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    number = serializers.CharField()
    term = serializers.IntegerField()
    self_education_hours = serializers.IntegerField(required=False, default=0)
    duration = serializers.ChoiceField(Theme.DURATION_CHOICES)
    discipline_name = serializers.CharField(
        read_only=True, source='discipline.short_name'
    )
    type_name = serializers.CharField(
        read_only=True, source='type.name'
    )

    audiences_count = serializers.IntegerField()
    teachers_count = serializers.IntegerField()

    type = serializers.PrimaryKeyRelatedField(
        queryset=ThemeType.objects
    )
    discipline = serializers.PrimaryKeyRelatedField(
        queryset=Discipline.objects
    )
    previous_themes = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects, many=True, required=False
    )

    teachers_main = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects, many=True
    )
    teachers_alternative = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects, many=True
    )
    audiences = serializers.PrimaryKeyRelatedField(
        queryset=Audience.objects, many=True
    )

    specialties = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects, many=True
    )

    class Meta:
        model = Theme
        exclude = [
            'created_at',
            'updated_at',
            'teachers'
        ]

    def create(self, validated_data):
        teachers_main = validated_data.pop('teachers_main')
        teachers_alternative = validated_data.pop('teachers_alternative')

        instance = super(ThemeSerializer, self).create(validated_data)
        self.Meta.model.set_teachers(instance, teachers_main,
                                     teachers_alternative)

        return instance

    def update(self, instance, validated_data):
        teachers_main = validated_data.pop('teachers_main')
        teachers_alternative = validated_data.pop('teachers_alternative')

        instance = super(ThemeSerializer, self).update(
            instance, validated_data
        )
        self.Meta.model.set_teachers(
            instance, teachers_main, teachers_alternative
        )

        return instance


class DisciplineSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    short_name = serializers.CharField()

    themes = ThemeSerializer(read_only=True, many=True)
    specialties = serializers.PrimaryKeyRelatedField(
        read_only=True, source='related_specialties_ids'
    )

    class Meta:
        model = Discipline
        exclude = [
            'created_at',
            'updated_at'
        ]


class TeacherSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    military_rank = serializers.CharField()
    work_hours_limit = serializers.IntegerField()

    class Meta:
        model = Teacher
        exclude = [
            'created_at',
            'updated_at'
        ]


class AudienceSerializer(serializers.ModelSerializer):
    description = serializers.CharField()
    location = serializers.CharField()

    class Meta:
        model = Audience
        exclude = [
            'created_at',
            'updated_at'
        ]


class ThemeTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    short_name = serializers.CharField()

    class Meta:
        model = ThemeType
        exclude = [
            'created_at',
            'updated_at'
        ]


class BuildScheduleSerializer(serializers.Serializer):
    start_date = serializers.DateField(write_only=True)
    term_length = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        Lesson.objects.all().delete()
        cache.set('current_term_load', 0, timeout=None)

        date = validated_data['start_date'].strftime('%Y-%m-%d')
        async = build_schedule.delay(date, validated_data['term_length'])

        cache.set('build_schedule', async.task_id, timeout=None)
        cache.set(
            'total_term_load', self.calc_total_term_load(), timeout=None
        )

        return async

    def calc_total_term_load(self):
        total = 0

        for specialty in Specialty.objects.all():
            for troop in specialty.troops.all():
                total += specialty.calc_course_length(troop.term)

        return total


class TeacherLoadStatisticsSerializer(serializers.Serializer):
    date_from = serializers.DateField(write_only=True)
    date_to = serializers.DateField(write_only=True)

    name = serializers.CharField(read_only=True)
    statistics = serializers.SerializerMethodField()

    def filter_lessons(self, teacher, date_from, date_to):
        return Lesson.objects.filter(
            date_of__gte=date_from,
            date_of__lte=date_to,
            teachers__id__in=[teacher.id]
        )

    def calc_teachers_load(self, teacher):
        lessons = self.filter_lessons(
            teacher, self.context['date_from'], self.context['date_to']
        )
        absolute = 0

        for lesson in lessons:
            if lesson.self_education:
                absolute += lesson.theme.self_education_hours
            else:
                absolute += lesson.theme.duration

        return absolute

    def get_statistics(self, teacher):
        absolute = self.calc_teachers_load(teacher)
        relative = float(absolute) / float(teacher.work_hours_limit)

        return {
            'absolute': absolute,
            'relative': relative
        }


class TroopProgressStatisticsSerializer(serializers.Serializer):
    code = serializers.CharField()
    statistics = serializers.SerializerMethodField()

    def calc_discipline_progress(self, troop, discipline):
        lessons = Lesson.objects.filter(
            troop=troop, theme__discipline=discipline
        )

        hours = 0
        for lesson in lessons:
            if lesson.self_education:
                hours += lesson.theme.self_education_hours
            else:
                hours += lesson.theme.duration

        course_length = discipline.calc_course_length(troop.term,
                                                      troop.specialty)

        if not course_length:
            return 1

        return float(hours) / float(course_length)

    def get_statistics(self, troop):
        progress_by_disciplines = []

        disciplines = troop.specialty.disciplines.all()

        for discipline in disciplines:
            progress_by_disciplines.append({
                'name': discipline.short_name,
                'progress': self.calc_discipline_progress(troop, discipline)
            })

        progress_summ = 0

        for discipline in progress_by_disciplines:
            progress_summ += discipline['progress']

        return {
            'total_progress': float(progress_summ) / float(
                len(progress_by_disciplines)
            ),
            'by_disciplines': progress_by_disciplines
        }


class TroopsProgressStatisticsSerializer(serializers.Serializer):
    code = serializers.CharField()
    disciplines = serializers.SerializerMethodField()

    def calc_discipline_progress(self, troop, discipline):
        lessons = Lesson.objects.filter(
            troop=troop, theme__discipline=discipline
        )

        hours = 0
        for lesson in lessons:
            if lesson.self_education:
                hours += lesson.theme.self_education_hours
            else:
                hours += lesson.theme.duration

        return float(hours) / float(discipline.calc_course_length(troop.term))

    def get_disciplines(self, troop):
        progress = []

        disciplines = troop.specialty.disciplines.all()

        for discipline in disciplines:
            progress.append({
                'name': discipline.short_name,
                'progress': self.calc_discipline_progress(troop, discipline)
            })

        return progress
