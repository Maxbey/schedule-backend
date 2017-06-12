# -*- coding: utf-8 -*-

from unittest import TestCase

from datetime import timedelta
from django.utils.timezone import now

from ..models import Lesson, Troop
from ..factories import TeacherFactory, AudienceFactory, DisciplineFactory, \
    ThemeFactory, LessonFactory, TroopFactory
from ..exporters import ExcelExporter


class ExcelExporterTest(TestCase):
    def tearDown(self):
        Lesson.objects.all().delete()
        Troop.objects.all().delete()

    def test_form_lesson_string(self):
        teacher_one = TeacherFactory(name=u'Ааа Ббб Ввв')
        teacher_two = TeacherFactory(name=u'Ггг Ддд Еее')

        audience_one = AudienceFactory(location='1-234')
        audience_two = AudienceFactory(location='5-678')

        discipline = DisciplineFactory(short_name=u'ЭкБТТ')
        theme = ThemeFactory(number='1.1', discipline=discipline)

        lesson = LessonFactory(
            theme=theme
        )
        lesson.teachers.set([teacher_one, teacher_two])
        lesson.audiences.set([audience_one, audience_two])

        result = ExcelExporter.form_lesson_string(lesson)
        expected_result = u'ЭкБТТ Т №1.1 кл 1-234, 5-678 Ааа, Ггг'

        self.assertEquals(
            result,
            expected_result
        )

    def test_group_lessons_by_date(self):
        earliest_date = (now() + timedelta(days=-2)).date()
        latest_date = (now() + timedelta(days=1)).date()

        lessons_one = LessonFactory.create_batch(2, date_of=latest_date)
        lessons_two = LessonFactory.create_batch(2, date_of=earliest_date)

        expected_result = [
            (earliest_date, lessons_two),
            (latest_date, lessons_one)
        ]
        result = ExcelExporter.group_lessons_by_date(Lesson.objects.all())
        self.assertEquals(result, expected_result)

    def test_group_lessons_by_troops(self):
        troop_one = TroopFactory(code='111', day=1)
        troop_two = TroopFactory(code='222', day=1)
        TroopFactory(code='333', day=1)

        earliest_date = (now() + timedelta(days=-2)).date()
        latest_date = (now() + timedelta(days=1)).date()

        lesson_one = LessonFactory(
            date_of=latest_date, troop=troop_two, initial_hour=4
        )
        lesson_two = LessonFactory(
            date_of=latest_date, troop=troop_one, initial_hour=4
        )
        lesson_five = LessonFactory(
            date_of=latest_date, troop=troop_one, initial_hour=0
        )

        lesson_three = LessonFactory(
            date_of=earliest_date, troop=troop_two, initial_hour=2
        )
        lesson_four = LessonFactory(
            date_of=earliest_date, troop=troop_one, initial_hour=4
        )
        lesson_six = LessonFactory(
            date_of=earliest_date, troop=troop_one, initial_hour=0
        )

        groups = [
            (earliest_date, [lesson_three, lesson_four, lesson_six]),
            (latest_date, [lesson_one, lesson_two, lesson_five])
        ]

        expected_result = [
            (earliest_date, [
                ('111', [lesson_six, lesson_four]),
                ('222', [lesson_three]),
                ('333', [])
            ]),
            (latest_date, [
                ('111', [lesson_five, lesson_two]),
                ('222', [lesson_one]),
                ('333', [])
            ])
        ]

        result = ExcelExporter.group_lessons_by_troops(groups)
        self.assertEquals(result, expected_result)
