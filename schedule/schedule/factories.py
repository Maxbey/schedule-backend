import random

import factory
from django.contrib.auth import get_user_model

from .models import Specialty, Troop, Discipline, Theme, Teacher


class SpecialtyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Specialty

    code = factory.Faker('word')


class TroopFactory(factory.DjangoModelFactory):
    class Meta:
        model = Troop

    code = factory.Faker('word')
    term = random.choice(range(1, 8))
    day = random.choice([1, 2, 3, 4, 5])

    specialty = factory.SubFactory(SpecialtyFactory)


class DisciplineFactory(factory.DjangoModelFactory):
    class Meta:
        model = Discipline

    full_name = factory.Faker('word')
    short_name = factory.Faker('word')


class ThemeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Theme

    name = factory.Faker('name')
    number = '1/2'
    term = 5
    self_education = random.choice([True, False])
    duration = random.choice([1, 2, 4, 6])

    audiences_count = 1
    teachers_count = 1

    discipline = factory.SubFactory(DisciplineFactory)


class TeacherFactory(factory.DjangoModelFactory):
    class Meta:
        model = Teacher

    name = factory.Faker('name')
    military_rank = factory.Faker('word')
    work_hours_limit = 300


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('user_name')
    email = factory.Faker('safe_email')
    password = 'pass'

    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)

        return manager.create_user(*args, **kwargs)

