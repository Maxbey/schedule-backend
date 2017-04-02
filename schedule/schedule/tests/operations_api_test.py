from datetime import timedelta
from django.utils.timezone import now
from rest_framework.test import APITestCase

from .data_api_test import ScheduleApiTestMixin
from ..factories import UserFactory, TeacherFactory, ThemeFactory, \
    LessonFactory, TroopFactory, DisciplineFactory, SpecialtyFactory


class TeacherLoadStatisticsApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/statistics/teachers_load/?date_from=%s&date_to=%s'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

    def test_get_statistics(self):
        teacher_one = TeacherFactory(work_hours_limit=30)
        teacher_two = TeacherFactory(work_hours_limit=60)

        theme = ThemeFactory(duration=6)

        for i in range(4):
            lesson_one = LessonFactory(date_of=now().date(), theme=theme)
            lesson_two = LessonFactory(date_of=now().date(), theme=theme)

            lesson_one.teachers.set([teacher_one])
            lesson_two.teachers.set([teacher_two])

        date_from = self.format_date(now() - timedelta(days=1))
        date_to = self.format_date(now() + timedelta(days=1))

        expected = [
            {
                'name': teacher_one.name,
                'statistics': {
                    'absolute': 24,
                    'relative': 0.8
                }
            },
            {
                'name': teacher_two.name,
                'statistics': {
                    'absolute': 24,
                    'relative': 0.4
                }
            }
        ]

        response = self.authorize_client(self.admin).get(
            self.url % (date_from, date_to)
        )

        self.assertEquals(response.json(), expected)


class TroopProgressStatisticsApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/statistics/troop/%i/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

    def test_get_statistics(self):
        specialty = SpecialtyFactory()
        troop = TroopFactory(specialty=specialty)

        discipline_one = DisciplineFactory()
        discipline_two = DisciplineFactory()

        specialty.disciplines.set([discipline_one, discipline_two])

        for i in range(6):
            ThemeFactory(discipline=discipline_one, duration=4)
            ThemeFactory(discipline=discipline_two, duration=2)

        self.create_lessons(troop, discipline_one, 2)
        self.create_lessons(troop, discipline_two, 4)

        expected = {
                'code': troop.code,
                'disciplines': [
                    {
                        'name': discipline_one.short_name,
                        'progress': 8.0 / 24
                    },
                    {
                        'name': discipline_two.short_name,
                        'progress': 8.0 / 12
                    }
                ]
            }

        response = self.authorize_client(self.admin).get(
            self.url % troop.id
        )

        self.assertEquals(response.json(), expected)

    def create_lessons(self, troop, discipline, count):
        themes = discipline.themes.all()[:count]

        for theme in themes:
            LessonFactory(troop=troop, theme=theme)
