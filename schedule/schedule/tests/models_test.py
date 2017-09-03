from unittest import TestCase

from ..factories import DisciplineFactory, ThemeFactory, SpecialtyFactory, TeacherFactory
from ..models import Theme, TeacherTheme


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

    def test_get_related_specialties_ids(self):
        specialties = SpecialtyFactory.create_batch(2)
        discipline = DisciplineFactory()

        for specialty in specialties:
            theme = ThemeFactory(discipline=discipline)
            theme.specialties.add(specialty)

        self.assertEquals(
            list(discipline.related_specialties_ids),
            [s.id for s in specialties]
        )


class ThemeModelTest(TestCase):
    def test_set_teachers(self):
        theme = ThemeFactory()

        teachers_main = TeacherFactory.create_batch(2)
        teachers_alternative = TeacherFactory.create_batch(2)

        Theme.set_teachers(theme, teachers_main, teachers_alternative)

        for teacher in teachers_main:
            self.assertFalse(teacher.teachertheme_set.first().alternative)

        for teacher in teachers_alternative:
            self.assertTrue(teacher.teachertheme_set.first().alternative)

    def test_get_teachers(self):
        theme = ThemeFactory()
        teachers = TeacherFactory.create_batch(2)

        TeacherTheme.objects.create(theme=theme, alternative=False, teacher=teachers[0])
        TeacherTheme.objects.create(theme=theme, alternative=True, teacher=teachers[1])

        self.assertEquals(list(theme.teachers_main), [teachers[0]])
        self.assertEquals(list(theme.teachers_alternative), [teachers[1]])
