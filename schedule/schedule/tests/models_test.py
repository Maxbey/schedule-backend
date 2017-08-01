from unittest import TestCase

from ..factories import DisciplineFactory, ThemeFactory, SpecialtyFactory


class SpecialtyModelTest(TestCase):
    def test_course_length_calculation(self):
        specialty = SpecialtyFactory()
        disciplines = DisciplineFactory.create_batch(2)
        term = 1

        for discipline in disciplines:
            themes = ThemeFactory.create_batch(
                2, discipline=discipline, self_education_hours=1,
                term=term, duration=4
            )
            for theme in themes:
                theme.specialties.set([specialty])

        another_specialty = SpecialtyFactory()
        another_theme = ThemeFactory(
            term=term, duration=6, self_education_hours=2,
            discipline = disciplines[0]
        )

        another_theme.specialties.set([another_specialty])
        self.assertEquals(specialty.calc_course_length(term), 20)


class DisciplineModelTest(TestCase):
    def test_course_length_calculation(self):
        specialty = SpecialtyFactory()
        discipline = DisciplineFactory()
        term = 1

        themes = ThemeFactory.create_batch(
            2, duration=2, self_education_hours=2,
            term=term, discipline=discipline
        )

        for theme in themes:
            theme.specialties.set([specialty])

        another_specialty = SpecialtyFactory()
        another_theme = ThemeFactory(
            term=term, duration=6, self_education_hours=2,
            discipline = discipline
        )

        another_theme.specialties.set([another_specialty])
        self.assertEquals(discipline.calc_course_length(term, specialty), 8)

    def test_get_course_length_filtered_by_term(self):
        specialty = SpecialtyFactory()
        discipline = DisciplineFactory()

        theme = ThemeFactory(
            duration=2, self_education_hours=2,
            term=3, discipline=discipline
        )
        theme.specialties.set([specialty])

        self.assertEquals(discipline.calc_course_length(1, specialty), 0)
