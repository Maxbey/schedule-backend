from unittest import TestCase

from ..factories import DisciplineFactory, ThemeFactory


class DisciplineModelTest(TestCase):
    def test_course_length(self):
        discipline = DisciplineFactory()
        ThemeFactory.create_batch(5, discipline=discipline, duration=4, term=1)

        self.assertEquals(discipline.calc_course_length(1), 20)
        self.assertEquals(discipline.calc_course_length(2), 0)