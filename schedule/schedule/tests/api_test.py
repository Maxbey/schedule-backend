from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from ..factories import UserFactory, SpecialtyFactory, TroopFactory


class ScheduleApiTestMixin(object):
    url = '/api/v1/specialty/'

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

        self.specialties = SpecialtyFactory.create_batch(2)
        TroopFactory.create_batch(2, specialty=self.specialties[0])

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
            ]
        }


class SpecialtyApiTest(ScheduleApiTestMixin, APITestCase):
    url = '/api/v1/specialty/'

    def test_get_list(self):
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
