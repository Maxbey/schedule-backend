from unittest import TestCase

from django.utils.timezone import now

from ..models import Lesson
from ..builder import ScheduleBuilder
from ..factories import LessonFactory, AudienceFactory, TeacherFactory, \
    ThemeFactory, TroopFactory, SpecialtyFactory, DisciplineFactory


class ScheduleBuilderTest(TestCase):
    def setUp(self):
        self.builder = ScheduleBuilder()
        Lesson.objects.all().delete()

    def test_find_free_audiences_should_be_found(self):
        audiences = AudienceFactory.create_batch(4)
        theme = ThemeFactory()
        theme.audiences.set(audiences)
        lessons = LessonFactory.create_batch(3)
        lessons[1].audiences.set(audiences[0:2])

        result = self.builder.find_free_audiences(
            theme, Lesson.objects.all()
        )

        self.assertEquals(result, audiences[2:4])

    def test_find_free_audiences_should_not_be_found(self):
        audiences = AudienceFactory.create_batch(4)
        theme = ThemeFactory()
        theme.audiences.set(audiences)
        lessons = LessonFactory.create_batch(3)
        lessons[1].audiences.set(audiences[0:2])
        lessons[2].audiences.set(audiences[2:4])

        result = self.builder.find_free_audiences(
            theme, Lesson.objects.all()
        )

        self.assertFalse(len(result))

    def test_find_free_teachers_should_be_found(self):
        teachers = TeacherFactory.create_batch(4)
        theme = ThemeFactory()
        theme.teachers.set(teachers)
        lessons = LessonFactory.create_batch(3)
        lessons[1].teachers.set(teachers[0:2])

        result = self.builder.find_free_teachers(
            theme, Lesson.objects.all()
        )

        self.assertEquals(result, teachers[2:4])

    def test_find_free_teachers_should_not_be_found(self):
        teachers = TeacherFactory.create_batch(4)
        theme = ThemeFactory()
        theme.teachers.set(teachers)
        lessons = LessonFactory.create_batch(3)
        lessons[1].teachers.set(teachers[0:2])
        lessons[2].teachers.set(teachers[2:4])

        result = self.builder.find_free_teachers(
            theme, Lesson.objects.all()
        )

        self.assertFalse(len(result))

    def test_calc_teacher_ratio(self):
        limit = 20
        teacher = TeacherFactory(work_hours_limit=limit)
        self.add_load_for_teacher(teacher, 6)

        result = self.builder.calc_teacher_ratio(teacher)
        self.assertEquals(result, float(6) / float(limit))

    def test_sort_teachers_by_priority(self):
        teachers = TeacherFactory.create_batch(3, work_hours_limit=100)

        self.add_load_for_teacher(teachers[2], 20)
        self.add_load_for_teacher(teachers[0], 40)
        self.add_load_for_teacher(teachers[1], 60)

        sorted = self.builder.sort_teachers_by_priority(teachers)
        expected = [
            teachers[2],
            teachers[0],
            teachers[1]
        ]

        self.assertEquals(sorted, expected)

    def test_get_lessons_in_same_time_should_be_found(self):
        troops = TroopFactory.create_batch(3)

        theme_one = ThemeFactory(duration=2)
        theme_two = ThemeFactory(duration=4)
        theme_three = ThemeFactory(duration=4)

        lesson_one = LessonFactory(
            initial_hour=2, theme=theme_one, troop=troops[0]
        )
        lesson_two = LessonFactory(
            initial_hour=0, theme=theme_two, troop=troops[1]
        )

        in_same_time = self.builder.get_lessons_in_same_time(
            theme_three, troops[2], now(), 0
        )

        self.assertEquals(in_same_time, [lesson_one, lesson_two])

    def test_get_lessons_in_same_time_should_not_be_found(self):
        troops = TroopFactory.create_batch(3)

        theme_one = ThemeFactory(duration=2)
        theme_two = ThemeFactory(duration=4)
        theme_three = ThemeFactory(duration=2)

        LessonFactory(
            initial_hour=2, theme=theme_one, troop=troops[0]
        )
        LessonFactory(
            initial_hour=0, theme=theme_two, troop=troops[1]
        )

        in_same_time = self.builder.get_lessons_in_same_time(
            theme_three, troops[2], now(), 4
        )

        self.assertFalse(len(in_same_time))

    def test_get_disciplines_by_priority(self):
        specialty = SpecialtyFactory()
        troop = TroopFactory(specialty=specialty)

        disciplines = DisciplineFactory.create_batch(3)

        for discipline in disciplines:
            discipline.specialties.set([specialty])
            self.create_course(discipline, 20)

        self.add_load_for_troop(troop, disciplines[2], 3)
        self.add_load_for_troop(troop, disciplines[0], 6)
        self.add_load_for_troop(troop, disciplines[1], 8)

        result = self.builder.get_disciplines_by_priority(troop)

        expected = [
            disciplines[2],
            disciplines[0],
            disciplines[1]
        ]

        self.assertEquals(result, expected)

    def test_get_next_theme(self):
        discipline = DisciplineFactory()
        troop = TroopFactory(term=3)

        theme_one = ThemeFactory(number='2/1', discipline=discipline, term=3)
        theme_two = ThemeFactory(number='1/1', discipline=discipline, term=3)
        theme_three = ThemeFactory(number='1/2', discipline=discipline, term=3)

        LessonFactory(theme=theme_two, troop=troop)
        LessonFactory(theme=theme_three, troop=troop)

        result = self.builder.get_next_theme(discipline, troop)

        self.assertEquals(theme_one, result)

    def create_course(self, discipline, hours):
        ThemeFactory.create_batch(hours / 2, duration=2, discipline=discipline)

    def add_load_for_troop(self, troop, discipline, lessons_count):
        themes = discipline.themes.all()

        for i in range(lessons_count):
            theme = themes[i]

            LessonFactory(
                troop=troop, theme=theme
            )

    def add_load_for_teacher(self, teacher, load):
        theme = ThemeFactory(duration=2)

        lessons = LessonFactory.create_batch(load / 2, theme=theme)

        for lesson in lessons:
            lesson.teachers.set([teacher])
