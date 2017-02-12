from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from ..models import Specialty, Troop, Discipline
from ..factories import UserFactory, SpecialtyFactory, TroopFactory, \
    DisciplineFactory


class ScheduleApiTestMixin(object):
    url = '/api/v1/specialty/'

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

            'specialties': self.get_ids(discipline.specialties.all())
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

    def test_creation(self):
        specialty = SpecialtyFactory(code='code')

        count_before = Troop.objects.count()
        payload = {
            'code': '321',
            'day': 1,
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
            'specialties': specialties_ids
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
