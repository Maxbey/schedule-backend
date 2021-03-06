from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum


class BaseScheduleModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Discipline(BaseScheduleModel):
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=40)

    @property
    def related_specialties_ids(self):
        return self.themes.values_list(
            'specialties', flat=True
        ).distinct()

    def calc_course_length(self, term, specialty):
        durations = self.get_courses_length(term, specialty)
        return durations[0] + durations[1]

    def get_courses_length(self, term, specialty):
        themes = self.themes.filter(
            term=term, specialties__in=[specialty]
        )
        if not themes.exists():
            return 0, 0

        duration = themes.aggregate(Sum('duration'))['duration__sum']
        self_ed = themes.aggregate(
            Sum('self_education_hours')
        )['self_education_hours__sum']

        return duration, self_ed

    def __unicode__(self):
        return self.full_name


class Specialty(BaseScheduleModel):
    code = models.CharField(max_length=30)

    @property
    def disciplines(self):
        ids = self.related_disciplines_ids

        return Discipline.objects.filter(id__in=ids)

    @property
    def related_disciplines_ids(self):
        return self.themes.values_list(
            'discipline', flat=True
        ).distinct()

    def calc_course_length(self, term):
        length = 0
        for discipline in self.disciplines:
            length += discipline.calc_course_length(term, self)

        return length

    def __unicode__(self):
        return self.code


class Troop(BaseScheduleModel):
    DAY_CHOICES = (
        (0, 'Mo'),
        (1, 'Tu'),
        (2, 'We'),
        (3, 'Th'),
        (4, 'Fr')
    )

    code = models.CharField(max_length=30)
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    term = models.PositiveSmallIntegerField()

    specialty = models.ForeignKey(Specialty)

    class Meta:
        default_related_name = 'troops'
        ordering = ['code']

    def __unicode__(self):
        return self.code


class ThemeType(BaseScheduleModel):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=30)

    def __unicode__(self):
        return '%s' % self.name


class Teacher(BaseScheduleModel):
    name = models.CharField(max_length=255)
    military_rank = models.CharField(max_length=100)
    work_hours_limit = models.PositiveIntegerField()

    class Meta:
        default_related_name = 'teachers'

    def __unicode__(self):
        return self.name


class Audience(BaseScheduleModel):
    description = models.CharField(max_length=255)
    location = models.CharField(max_length=40)

    class Meta:
        default_related_name = 'audiences'

    def __unicode__(self):
        return self.location


class TeacherTheme(models.Model):
    teacher = models.ForeignKey(Teacher)
    theme = models.ForeignKey('Theme')
    alternative = models.BooleanField(default=False)


class Theme(BaseScheduleModel):
    DURATION_CHOICES = (
        (1, 1),
        (2, 2),
        (4, 4),
        (6, 6)
    )

    name = models.CharField(max_length=255)
    number = models.CharField(max_length=30)
    term = models.PositiveSmallIntegerField()
    self_education_hours = models.PositiveSmallIntegerField(default=0)
    duration = models.PositiveSmallIntegerField(choices=DURATION_CHOICES)

    audiences = models.ManyToManyField(Audience)
    teachers = models.ManyToManyField(Teacher, through=TeacherTheme)

    audiences_count = models.PositiveSmallIntegerField()
    teachers_count = models.PositiveSmallIntegerField()
    specialties = models.ManyToManyField(Specialty)
    discipline = models.ForeignKey(Discipline)
    type = models.ForeignKey(ThemeType, on_delete=models.SET_NULL, null=True)
    previous_themes = models.ManyToManyField('self', symmetrical=False)

    @property
    def teachers_main(self):
        return self.teachers.filter(teachertheme__alternative=False)

    @property
    def teachers_alternative(self):
        return self.teachers.filter(teachertheme__alternative=True)

    @staticmethod
    def set_teachers(theme, main_teachers, alternative_teachers):
        theme.teachers.clear()
        through = theme.teachers.through

        for teacher in main_teachers:
            through.objects.create(teacher=teacher, theme=theme, alternative=False)

        for teacher in alternative_teachers:
            through.objects.create(teacher=teacher, theme=theme, alternative=True)

    class Meta:
        default_related_name = 'themes'
        ordering = ['number']

    def __unicode__(self):
        return '%s %s' % (self.number, self.name)


class Lesson(BaseScheduleModel):
    date_of = models.DateField()
    initial_hour = models.PositiveSmallIntegerField()

    troop = models.ForeignKey(Troop)
    theme = models.ForeignKey(Theme)

    teachers = models.ManyToManyField(Teacher)
    audiences = models.ManyToManyField(Audience)

    self_education = models.BooleanField(default=False)

    class Meta:
        default_related_name = 'lessons'

    def __unicode__(self):
        discipline_name = self.theme.discipline.short_name

        return '%s %s %s' % (
            discipline_name, self.theme.number, self.troop.code
        )
