from datetime import timedelta, datetime
from django.utils.timezone import now
from mock import patch, Mock, call
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
        term = 4

        self.troop_one = TroopFactory(specialty=specialty, term=term)
        self.troop_two = TroopFactory(specialty=specialty, term=term)

        self.discipline_one = DisciplineFactory()
        self.discipline_two = DisciplineFactory()

        for i in range(6):
            ThemeFactory(
                discipline=self.discipline_one, duration=4, term=term
            ).specialties.set([specialty])
            ThemeFactory(
                discipline=self.discipline_two, duration=2, term=term
            ).specialties.set([specialty])

        self.create_lessons(self.troop_one, self.discipline_one, 2)
        self.create_lessons(self.troop_one, self.discipline_two, 4)

        self.create_lessons(self.troop_two, self.discipline_one, 4)
        self.create_lessons(self.troop_two, self.discipline_two, 2)

    def test_get_statistics(self):
        expected = {
                'code': self.troop_one.code,
                'statistics': {
                    'total_progress': (8.0 / 36 + 8.0 / 24) / 2.0,
                    'by_disciplines': [
                        {
                            'name': self.discipline_one.short_name,
                            'progress': 8.0 / 36
                        },
                        {
                            'name': self.discipline_two.short_name,
                            'progress': 8.0 / 24
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
                    'total_progress': (8.0 / 36 + 8.0 / 24) / 2.0,
                    'by_disciplines': [
                        {
                            'name': self.discipline_one.short_name,
                            'progress': 8.0 / 36
                        },
                        {
                            'name': self.discipline_two.short_name,
                            'progress': 8.0 / 24
                        }
                    ]
                }
            },
            {
                'code': self.troop_two.code,
                'statistics': {
                    'total_progress': (16.0 / 36 + 4.0 / 24) / 2.0,
                    'by_disciplines': [
                        {
                            'name': self.discipline_one.short_name,
                            'progress': 16.0 / 36
                        },
                        {
                            'name': self.discipline_two.short_name,
                            'progress': 4.0 / 24
                        }
                    ]
                }
            }
        ]

        response = self.authorize_client(self.admin).get(
            self.url
        )

        self.assertEquals(
            response.json(),
            sorted(expected, key=lambda troop: troop['code'])
        )

    def create_lessons(self, troop, discipline, count):
        themes = discipline.themes.filter(term=troop.term)[:count]

        for theme in themes:
            LessonFactory(troop=troop, theme=theme)


class ScheduleApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/schedule/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

    @patch('schedule.api.serializers.cache')
    @patch('schedule.api.serializers.build_schedule')
    def test_schedule_create(self, build_schedule, cache):
        specialty = SpecialtyFactory()
        troop = TroopFactory(specialty=specialty, term=2)
        discipline = DisciplineFactory()
        themes = ThemeFactory.create_batch(
            2, duration=6, term=2, discipline=discipline,
            self_education_hours=1
        )

        for theme in themes:
            theme.specialties.set([specialty])
            LessonFactory(theme=theme, troop=troop)

        payload = {
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'term_length': 18
        }
        async_result = Mock(task_id=1)
        build_schedule.delay.return_value = async_result

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )

        build_schedule.delay.assert_called_once_with(
            payload['start_date'], payload['term_length']
        )

        calls = [
            call('current_term_load', 0, timeout=None),
            call('build_schedule', async_result.task_id, timeout=None),
            call('total_term_load', 14, timeout=None)
        ]

        cache.set.assert_has_calls(calls)
        self.assertEquals(response.status_code, 201)
