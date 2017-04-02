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

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json(), expected)


class TroopProgressStatisticsApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/statistics/troop/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        specialty = SpecialtyFactory()
        self.troop_one = TroopFactory(specialty=specialty)
        self.troop_two = TroopFactory(specialty=specialty)

        self.discipline_one = DisciplineFactory()
        self.discipline_two = DisciplineFactory()

        specialty.disciplines.set([self.discipline_one, self.discipline_two])

        for i in range(6):
            ThemeFactory(discipline=self.discipline_one, duration=4)
            ThemeFactory(discipline=self.discipline_two, duration=2)

        self.create_lessons(self.troop_one, self.discipline_one, 2)
        self.create_lessons(self.troop_one, self.discipline_two, 4)

        self.create_lessons(self.troop_two, self.discipline_one, 4)
        self.create_lessons(self.troop_two, self.discipline_two, 2)

    def test_get_statistics(self):
        expected = {
                'code': self.troop_one.code,
                'statistics': {
                    'total_progress': (8.0 / 24 + 8.0 / 12) / 2.0,
                    'by_disciplines': [
                        {
                            'name': self.discipline_one.short_name,
                            'progress': 8.0 / 24
                        },
                        {
                            'name': self.discipline_two.short_name,
                            'progress': 8.0 / 12
                        }
                    ]
                }
            }

        url = self.url + '%i/'
        response = self.authorize_client(self.admin).get(
            url % self.troop_one.id
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json(), expected)

    def test_list_statistics(self):
        expected = [
            {
                'code': self.troop_one.code,
                'statistics': {
                    'total_progress': (8.0 / 24 + 8.0 / 12) / 2.0,
                    'by_disciplines': [
                        {
                            'name': self.discipline_one.short_name,
                            'progress': 8.0 / 24
                        },
                        {
                            'name': self.discipline_two.short_name,
                            'progress': 8.0 / 12
                        }
                    ]
                }
            },
            {
                'code': self.troop_two.code,
                'statistics': {
                    'total_progress': (16.0 / 24 + 4.0 / 12) / 2.0,
                    'by_disciplines': [
                        {
                            'name': self.discipline_one.short_name,
                            'progress': 16.0 / 24
                        },
                        {
                            'name': self.discipline_two.short_name,
                            'progress': 4.0 / 12
                        }
                    ]
                }
            }
        ]

        response = self.authorize_client(self.admin).get(
            self.url
        )

        self.assertEquals(response.json(), expected)

    def create_lessons(self, troop, discipline, count):
        themes = discipline.themes.all()[:count]

        for theme in themes:
            LessonFactory(troop=troop, theme=theme)
