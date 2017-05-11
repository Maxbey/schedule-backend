from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum


class BaseScheduleModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Specialty(BaseScheduleModel):
    code = models.CharField(max_length=30)

    @property
    def course_length(self):
        length = 0
        for discipline in self.disciplines.all():
            length += discipline.course_length

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

    specialty = models.ForeignKey(Specialty, related_name='troops')

    def __unicode__(self):
        return self.code


class Discipline(BaseScheduleModel):
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=40)

    specialties = models.ManyToManyField(Specialty, related_name='disciplines')

    @property
    def course_length(self):
        return self.themes.aggregate(Sum('duration'))['duration__sum']

    def __unicode__(self):
        return self.full_name


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

    discipline = models.ForeignKey(Discipline, related_name='themes')
    type = models.ForeignKey(
        ThemeType, related_name='themes',
        on_delete=models.SET_NULL, null=True
    )
    previous_themes = models.ManyToManyField('self', symmetrical=False)

    def __unicode__(self):
        return '%s %s' % (self.number, self.name)


class Teacher(BaseScheduleModel):
    name = models.CharField(max_length=255)
    military_rank = models.CharField(max_length=100)
    work_hours_limit = models.PositiveIntegerField()

    themes = models.ManyToManyField(Theme, related_name='teachers')

    def __unicode__(self):
        return self.name


class Audience(BaseScheduleModel):
    description = models.CharField(max_length=255)
    location = models.CharField(max_length=40)

    themes = models.ManyToManyField(Theme, related_name='audiences')

    def __unicode__(self):
        return self.location


class Lesson(BaseScheduleModel):
    date_of = models.DateField()
    initial_hour = models.PositiveSmallIntegerField()

    troop = models.ForeignKey(Troop, related_name='lessons')
    theme = models.ForeignKey(Theme, related_name='lessons')

    teachers = models.ManyToManyField(Teacher, related_name='lessons')
    audiences = models.ManyToManyField(Audience, related_name='lessons')

    def __unicode__(self):
        discipline_name = self.theme.discipline.short_name

        return '%s %s %s' % (
            discipline_name, self.theme.number, self.troop.code
        )
