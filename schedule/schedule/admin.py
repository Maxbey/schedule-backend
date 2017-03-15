from django.contrib import admin

from .models import Specialty, Troop, Discipline, Theme, Teacher, Audience, \
    Lesson, ThemeType

admin.site.register(Specialty)
admin.site.register(Troop)
admin.site.register(Discipline)
admin.site.register(Theme)
admin.site.register(Teacher)
admin.site.register(Audience)
admin.site.register(Lesson)
admin.site.register(ThemeType)
