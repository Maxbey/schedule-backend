from unittest import TestCase

from ..factories import DisciplineFactory, ThemeFactory


class DisciplineModelTest(TestCase):
    def test_course_length(self):
        discipline = DisciplineFactory()
        ThemeFactory.create_batch(5, discipline=discipline, duration=4)

        self.assertEquals(discipline.course_length, 20)