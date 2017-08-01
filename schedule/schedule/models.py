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

    def calc_course_length(self, term, specialty):
        themes = self.themes.filter(
            term=term, specialties__in=[specialty]
        )
        if not themes.exists():
            return 0

        duration = themes.aggregate(Sum('duration'))['duration__sum']
        self_ed = themes.aggregate(
            Sum('self_education_hours')
        )['self_education_hours__sum']

        return duration + self_ed

    def __unicode__(self):
        return self.full_name


class Specialty(BaseScheduleModel):
    code = models.CharField(max_length=30)

    @property
    def disciplines(self):
        ids = self.themes.values_list(
            'discipline', flat=True
        ).distinct()

        return Discipline.objects.filter(id__in=ids)

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

    audiences_count = models.PositiveSmallIntegerField()
    teachers_count = models.PositiveSmallIntegerField()
    specialties = models.ManyToManyField(Specialty)
    discipline = models.ForeignKey(Discipline)
    type = models.ForeignKey(ThemeType, on_delete=models.SET_NULL, null=True)
    previous_themes = models.ManyToManyField('self', symmetrical=False)

    class Meta:
        default_related_name = 'themes'
        ordering = ['number']

    def __unicode__(self):
        return '%s %s' % (self.number, self.name)


class Teacher(BaseScheduleModel):
    name = models.CharField(max_length=255)
    military_rank = models.CharField(max_length=100)
    work_hours_limit = models.PositiveIntegerField()

    themes = models.ManyToManyField(Theme)

    class Meta:
        default_related_name = 'teachers'

    def __unicode__(self):
        return self.name


class Audience(BaseScheduleModel):
    description = models.CharField(max_length=255)
    location = models.CharField(max_length=40)

    themes = models.ManyToManyField(Theme)

    class Meta:
        default_related_name = 'audiences'

    def __unicode__(self):
        return self.location


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
