from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from ..models import Specialty, Troop, Discipline, Theme, Teacher, Audience, \
    ThemeType
from ..factories import UserFactory, SpecialtyFactory, TroopFactory, \
    DisciplineFactory, ThemeFactory, TeacherFactory, AudienceFactory, \
    ThemeTypeFactory


class ScheduleApiTestMixin(object):

    def test_when_unathorized(self):
        response = self.client.get(self.url)

        self.assertEquals(response.status_code, 401)
        self.assertEquals(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'}
        )

    def test_when_common_user(self):
        user = UserFactory()

        response = self.authorize_client(user).get(self.url)

        self.assertEquals(response.status_code, 403)
        self.assertEquals(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def authorize_client(self, user):
        token = Token.objects.create(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        return client

    def get_ids(self, items):
        return [item.id for item in items]

    def serialize_troop(self, troop):
        return {
            'id': troop.id,
            'code': troop.code,
            'term': troop.term,
            'day': troop.day,

            'specialty': troop.specialty.id,
            'specialty_code': troop.specialty.code
        }

    def serialize_specialty(self, specialty):
        return {
            'id': specialty.id,
            'code': specialty.code,

            'troops': [
                self.serialize_troop(troop) for troop in specialty.troops.all()
            ],
            'disciplines': self.get_ids(specialty.disciplines.all())
        }

    def serialize_discipline(self, discipline):
        return {
            'id': discipline.id,
            'full_name': discipline.full_name,
            'short_name': discipline.short_name,

            'specialties': self.get_ids(discipline.specialties.all()),
            'themes': [
                self.serialize_theme(theme)
                for theme in discipline.themes.all()
            ]
        }

    def serialize_theme(self, theme):
        return {
            'id': theme.id,
            'name': theme.name,
            'number': theme.number,
            'term': theme.term,
            'self_education': theme.self_education,
            'duration': theme.duration,
            'audiences_count': theme.audiences_count,
            'teachers_count': theme.teachers_count,
            'discipline': theme.discipline.id,
            'discipline_name': theme.discipline.short_name,
            'type': theme.type.id,
            'type_name': theme.type.name,
            'previous_themes': self.get_ids(theme.previous_themes.all()),
            'teachers': self.get_ids(theme.teachers.all()),
            'audiences': self.get_ids(theme.audiences.all())
        }

    def serialize_teacher(self, teacher):
        return {
            'id': teacher.id,
            'name': teacher.name,
            'military_rank': teacher.military_rank,
            'work_hours_limit': teacher.work_hours_limit
        }

    def serialize_audience(self, audience):
        return {
            'id': audience.id,
            'description': audience.description,
            'location': audience.location
        }

    def serialize_theme_type(self, theme_type):
        return {
            'id': theme_type.id,
            'name': theme_type.name,
            'short_name': theme_type.short_name
        }


class SpecialtyApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/specialty/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.disciplines = DisciplineFactory.create_batch(2)
        self.specialties = SpecialtyFactory.create_batch(2)

        TroopFactory.create_batch(2, specialty=self.specialties[0])

    def test_get_list(self):
        for specialty in self.specialties:
            specialty.disciplines.set(self.disciplines)

        response = self.authorize_client(self.admin).get(self.url)

        expected_response = [
            self.serialize_specialty(specialty)
            for specialty in self.specialties
        ]

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            expected_response
        )

    def test_searching(self):
        specialty = SpecialtyFactory(code='specific')
        url = self.url + '?search=specif'

        response = self.authorize_client(self.admin).get(url)
        response_data = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_data), 1)
        self.assertEquals(
            response_data,
            [self.serialize_specialty(specialty)]
        )

    def test_creation(self):
        count_before = Specialty.objects.count()
        disciplines = DisciplineFactory.create_batch(2)
        disciplines_ids = self.get_ids(disciplines)

        payload = {
            'code': '420700',
            'disciplines': disciplines_ids
        }

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )
        response_data = response.json()
        id = response_data.pop('id')

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_data, {
            'code': payload['code'],
            'troops': [],
            'disciplines': disciplines_ids
        })

        self.assertEquals(count_before + 1, Specialty.objects.count())
        self.assertEquals(
            Specialty.objects.get(pk=id).code,
            payload['code']
        )
        self.assertEquals(
            list(Specialty.objects.get(pk=id).disciplines.all()),
            disciplines
        )


class TroopApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/troop/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.troops = TroopFactory.create_batch(2)

    def test_get_list(self):
        response = self.authorize_client(self.admin).get(self.url)
        expected_response = [
            self.serialize_troop(troop)
            for troop in self.troops
        ]

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            expected_response
        )

    def test_searching(self):
        troop = TroopFactory(code='specific')
        url = self.url + '?search=specif'

        response = self.authorize_client(self.admin).get(url)
        response_data = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_data), 1)
        self.assertEquals(
            response_data,
            [self.serialize_troop(troop)]
        )

    def test_creation(self):
        specialty = SpecialtyFactory(code='code')

        count_before = Troop.objects.count()
        payload = {
            'code': '321',
            'day': 0,
            'term': 5,
            'specialty': specialty.id
        }

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )

        response_data = response.json()
        id = response_data.pop('id')

        payload['specialty_code'] = specialty.code

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_data, payload)

        self.assertEquals(count_before + 1, Troop.objects.count())
        self.assertEquals(
            Troop.objects.get(pk=id).code,
            payload['code']
        )


class DisciplineApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/discipline/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.disciplines = DisciplineFactory.create_batch(2)
        self.specialties = SpecialtyFactory.create_batch(2)
        self.themes = ThemeFactory.create_batch(
            2, discipline=self.disciplines[0]
        )

    def test_get_list(self):
        for discipline in self.disciplines:
            discipline.specialties.set(self.specialties)

        response = self.authorize_client(self.admin).get(self.url)
        expected_response = [
            self.serialize_discipline(discipline)
            for discipline in self.disciplines
        ]

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            expected_response
        )

    def test_searching(self):
        discipline = DisciplineFactory(short_name='specific')
        url = self.url + '?search=specif'

        response = self.authorize_client(self.admin).get(url)
        response_data = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_data), 1)
        self.assertEquals(
            response_data,
            [self.serialize_discipline(discipline)]
        )

    def test_creation(self):
        count_before = Discipline.objects.count()
        specialties = SpecialtyFactory.create_batch(2)
        specialties_ids = self.get_ids(specialties)

        payload = {
            'full_name': 'some long name',
            'short_name': 'short name',
            'specialties': specialties_ids
        }

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )

        response_data = response.json()
        id = response_data.pop('id')

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_data, {
            'full_name': payload['full_name'],
            'short_name': payload['short_name'],
            'specialties': specialties_ids,
            'themes': []
        })

        self.assertEquals(count_before + 1, Discipline.objects.count())
        self.assertEquals(
            Discipline.objects.get(pk=id).full_name,
            payload['full_name']
        )

        self.assertEquals(
            list(Discipline.objects.get(pk=id).specialties.all()),
            specialties
        )


class ThemeApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/theme/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.themes = ThemeFactory.create_batch(2)
        self.prev_themes = ThemeFactory.create_batch(2)

    def test_get_list(self):
        teachers = TeacherFactory.create_batch(2)
        audiences = AudienceFactory.create_batch(2)

        for theme in self.themes:
            theme.previous_themes.set(self.prev_themes)
            theme.teachers.set(teachers)
            theme.audiences.set(audiences)

        response = self.authorize_client(self.admin).get(self.url)

        expected_themes = [
            self.serialize_theme(theme)
            for theme in self.themes
        ]
        expected_prev = [
            self.serialize_theme(theme)
            for theme in self.prev_themes
        ]

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            expected_themes + expected_prev
        )

    def test_searching(self):
        theme = ThemeFactory(name='specific')
        url = self.url + '?search=specif'

        response = self.authorize_client(self.admin).get(url)
        response_data = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_data), 1)
        self.assertEquals(
            response_data,
            [self.serialize_theme(theme)]
        )

    def test_creation(self):
        discipline = DisciplineFactory()
        theme_type = ThemeTypeFactory()
        teachers = TeacherFactory.create_batch(2)
        audiences = AudienceFactory.create_batch(2)

        count_before = Theme.objects.count()
        payload = {
            'name': 'Some Theme Name',
            'number': '1/1',
            'term': 5,
            'self_education': False,
            'duration': 2,
            'audiences_count': 1,
            'teachers_count': 1,
            'discipline': discipline.id,
            'type': theme_type.id,
            'previous_themes': self.get_ids(self.prev_themes),
            'teachers': self.get_ids(teachers),
            'audiences': self.get_ids(audiences)
        }

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )

        response_data = response.json()
        id = response_data.pop('id')
        payload['discipline_name'] = discipline.short_name
        payload['type_name'] = theme_type.name

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_data, payload)

        self.assertEquals(count_before + 1, Theme.objects.count())
        self.assertEquals(
            Theme.objects.get(pk=id).name,
            payload['name']
        )

        self.assertEquals(
            list(Theme.objects.get(pk=id).previous_themes.all()),
            self.prev_themes
        )
        self.assertEquals(
            list(Theme.objects.get(pk=id).teachers.all()),
            teachers
        )

        self.assertEquals(
            list(Theme.objects.get(pk=id).audiences.all()),
            audiences
        )


class TeacherApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/teacher/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.teachers = TeacherFactory.create_batch(2)

    def test_get_list(self):
        response = self.authorize_client(self.admin).get(self.url)

        expected_response = [
            self.serialize_teacher(teacher)
            for teacher in self.teachers
        ]

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            expected_response
        )

    def test_searching(self):
        teacher = TeacherFactory(name='specific')
        url = self.url + '?search=specif'

        response = self.authorize_client(self.admin).get(url)
        response_data = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_data), 1)
        self.assertEquals(
            response_data,
            [self.serialize_teacher(teacher)]
        )

    def test_creation(self):
        count_before = Teacher.objects.count()

        payload = {
            'name': 'Some Name',
            'military_rank': 'Some rank',
            'work_hours_limit': 300
        }

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )

        response_data = response.json()
        id = response_data.pop('id')

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_data, payload)

        self.assertEquals(count_before + 1, Teacher.objects.count())
        self.assertEquals(
            Teacher.objects.get(pk=id).name,
            payload['name']
        )


class AudienceApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/audience/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.audiences = AudienceFactory.create_batch(2)

    def test_get_list(self):
        response = self.authorize_client(self.admin).get(self.url)

        expected_response = [
            self.serialize_audience(audience)
            for audience in self.audiences
        ]

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            expected_response
        )

    def test_searching(self):
        audience = AudienceFactory(location='specific')
        url = self.url + '?search=specif'

        response = self.authorize_client(self.admin).get(url)
        response_data = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_data), 1)
        self.assertEquals(
            response_data,
            [self.serialize_audience(audience)]
        )

    def test_creation(self):
        count_before = Audience.objects.count()

        payload = {
            'description': 'Some description',
            'location': '3-407'
        }

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )

        response_data = response.json()
        id = response_data.pop('id')

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_data, payload)

        self.assertEquals(count_before + 1, Audience.objects.count())
        self.assertEquals(
            Audience.objects.get(pk=id).location,
            payload['location']
        )


class ThemeTypeApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/theme_type/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.types = ThemeTypeFactory.create_batch(2)

    def test_get_list(self):
        response = self.authorize_client(self.admin).get(self.url)

        expected_response = [
            self.serialize_theme_type(theme_type)
            for theme_type in self.types
        ]

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            expected_response
        )

    def test_searching(self):
        theme_type = ThemeTypeFactory(name='specific')
        url = self.url + '?search=specif'

        response = self.authorize_client(self.admin).get(url)
        response_data = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_data), 1)
        self.assertEquals(
            response_data,
            [self.serialize_theme_type(theme_type)]
        )

    def test_creation(self):
        count_before = ThemeType.objects.count()

        payload = {
            'name': 'Some full name',
            'short_name': 'sm-shrt'
        }

        response = self.authorize_client(self.admin).post(
            self.url, data=payload
        )

        response_data = response.json()
        id = response_data.pop('id')

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_data, payload)

        self.assertEquals(count_before + 1, ThemeType.objects.count())
        self.assertEquals(
            ThemeType.objects.get(pk=id).short_name,
            payload['short_name']
        )