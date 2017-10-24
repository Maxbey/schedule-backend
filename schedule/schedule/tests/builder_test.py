from unittest import TestCase

from django.utils.timezone import now

from ..models import Lesson, Theme
from ..builder import VariationsBuilder
from ..factories import LessonFactory, AudienceFactory, TeacherFactory, \
    ThemeFactory, TroopFactory, SpecialtyFactory, DisciplineFactory


class VariationsBuilderTest(TestCase):
    def setUp(self):
        self.builder = VariationsBuilder()

    def test_test(self):
        specialty = SpecialtyFactory(code='300')

        discipline_one = DisciplineFactory(short_name='TTO')
        discipline_two = DisciplineFactory(short_name='YOBP')
        discipline_three = DisciplineFactory(short_name='Rem')

        theme_one = ThemeFactory(
            duration=2, discipline=discipline_one, term=1, number='1.1'
        )
        theme_one1 = ThemeFactory(
            duration=2, discipline=discipline_one, term=1, number='1.2'
        )
        theme_two = ThemeFactory(
            duration=2, discipline=discipline_two, term=1, number='1.1'
        )
        theme_two2 = ThemeFactory(
            duration=2, discipline=discipline_two, term=1, number='1.2'
        )
        theme_three = ThemeFactory(
            duration=2, discipline=discipline_three, term=1, number='1.1'
        )
        theme_three2 = ThemeFactory(
            duration=2, discipline=discipline_three, term=1, number='1.2'
        )

        for theme in [theme_one, theme_two, theme_three]:
            theme.specialties.set([specialty])

        result = self.builder.build_variations_for_specialty(specialty, 1)
        import pudb; pu.db
        a = ''
