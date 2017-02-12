from __future__ import unicode_literals

from django.db import models


class BaseScheduleModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Specialty(BaseScheduleModel):
    code = models.CharField(max_length=30)

    def __unicode__(self):
        return self.code


class Troop(BaseScheduleModel):
    DAY_CHOICES = (
        (1, 'Mo'),
        (2, 'Tu'),
        (3, 'We'),
        (4, 'Th'),
        (5, 'Fr')
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

    def __unicode__(self):
        return self.full_name