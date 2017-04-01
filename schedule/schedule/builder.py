from datetime import timedelta
from django.core.cache import cache

from .models import Lesson, Troop


class ScheduleBuilder(object):
    hours_per_day = 6

    def build(self, date, term_length):
        cache.set('current_term_load', 0)

        for i in range(term_length):
            for troop in Troop.objects.all().order_by('code'):
                date = date - timedelta(days=date.weekday())
                date = date + timedelta(days=troop.day)
                hours = 0

                while hours != self.hours_per_day:
                    disciplines = self.get_disciplines_by_priority(troop)

                    lesson_dependencies = self.find_lesson_dependencies(
                        disciplines, troop, date, hours
                    )

                    if lesson_dependencies is None:
                        break

                    theme, teachers, audiences = lesson_dependencies

                    lesson = Lesson.objects.create(
                        date_of=date, initial_hour=hours,
                        troop=troop, theme=theme,
                    )

                    lesson.teachers.set(teachers)
                    lesson.audiences.set(audiences)

                    hours += theme.duration
                    cache.set(
                        'current_term_load',
                        int(cache.get('current_term_load')) + theme.duration
                    )

            date = date + timedelta(weeks=1)

    def find_lesson_dependencies(self, disciplines, troop, date, initial_hour):
        if disciplines[0][1] == 1:
            return None

        themes = self.fetch_disciplines_head_themes(
            troop, initial_hour, disciplines
        )

        while True:
            if not len(themes):
                return None

            theme = themes[0]

            if not self.check_prev_themes(theme, troop):
                themes.pop(0)
                continue

            lessons_in_same_time = self.get_lessons_in_same_time(
                theme, troop, date, initial_hour
            )

            if self.is_theme_parallel(theme, lessons_in_same_time) \
                    and len(themes) > 1:
                themes.pop(0)
                continue

            teachers_not_enough = False
            audiences_not_enough = False

            found_teachers = self.find_free_teachers(
                theme, lessons_in_same_time
            )

            if len(found_teachers) < theme.teachers_count:
                if len(themes) > 1:
                    themes.pop(0)
                    continue

                teachers_not_enough = True

            found_audiences = self.find_free_audiences(
                theme, lessons_in_same_time
            )

            if len(found_audiences) < theme.audiences_count:
                if len(themes) > 1:
                    themes.pop(0)
                    continue

                audiences_not_enough = True

            if not teachers_not_enough:
                teachers = found_teachers[0:theme.teachers_count]
            else:
                teachers = []

            if not audiences_not_enough:
                audiences = found_audiences[0:theme.audiences_count]
            else:
                audiences = []

            return theme, teachers, audiences

    def fetch_disciplines_head_themes(self, troop, initial_hour, disciplines):
        themes = []

        for discipline in disciplines:
            next_theme = self.get_next_theme(discipline[0], troop)
            if next_theme:
                themes.append(
                    next_theme
                )

        return [
            theme for theme in themes
            if not (theme.duration + initial_hour > self.hours_per_day)
        ]

    def calc_teacher_ratio(self, teacher):
        hours = 0

        for lesson in teacher.lessons.all():
            hours += lesson.theme.duration

        return float(hours) / float(teacher.work_hours_limit)

    def sort_teachers_by_priority(self, teachers):
        with_ratio = []

        for teacher in teachers:
            with_ratio.append((teacher, self.calc_teacher_ratio(teacher)))

        sorted_by_ratio = sorted(with_ratio, key=lambda tup: tup[1])

        return [teacher[0] for teacher in sorted_by_ratio]

    def get_disciplines_by_priority(self, troop):
        with_ratio = []

        for discipline in troop.specialty.disciplines.all():
            hours = 0

            for theme in discipline.themes.all():
                if Lesson.objects.filter(troop=troop, theme=theme).exists():
                    hours += theme.duration

            with_ratio.append(
                (discipline, float(hours) / float(discipline.course_length))
            )

        return sorted(with_ratio, key=lambda tup: tup[1])

    def get_next_theme(self, discipline, troop):
        themes = discipline.themes.filter(term=troop.term)
        sorted_by_number = sorted(
            themes, key=lambda theme: float(theme.number)
        )

        for theme in sorted_by_number:
            if not Lesson.objects.filter(troop=troop, theme=theme).exists():
                return theme

    def check_prev_themes(self, theme, troop):
        if not theme.previous_themes.count():
            return True

        for previous_theme in theme.previous_themes.all():
            if not Lesson.objects.filter(
                    troop=troop, theme=previous_theme
            ).exists():
                return False

        return True

    def get_lessons_in_same_time(self, theme, troop, date, initial_hour):
        in_same_time = []

        time_line = set(range(initial_hour, initial_hour + theme.duration))
        in_same_day = Lesson.objects.filter(date_of=date).exclude(troop=troop)

        for lesson in in_same_day:
            end_hour = lesson.initial_hour + lesson.theme.duration
            current_time_line = set(range(lesson.initial_hour + 1, end_hour))

            if len(time_line & current_time_line):
                in_same_time.append(lesson)

        return in_same_time

    def is_theme_parallel(self, theme, lessons_in_same_time):
        return theme in [lesson.theme for lesson in lessons_in_same_time]

    def is_audience_free(self, required_audience, lessons_in_same_time):
        for lesson in lessons_in_same_time:
            if required_audience in lesson.audiences.all():
                return False

        return True

    def find_free_audiences(self, theme, lessons_in_same_time):
        free = []

        for audience in theme.audiences.all():
            if self.is_audience_free(audience, lessons_in_same_time):
                free.append(audience)

        return free

    def is_teacher_free(self, required_teacher, lessons_in_same_time):
        for lesson in lessons_in_same_time:
            if required_teacher in lesson.teachers.all():
                return False

        return True

    def find_free_teachers(self, theme, lessons_in_same_time):
        free = []

        for teacher in theme.teachers.all():
            if self.is_teacher_free(teacher, lessons_in_same_time):
                free.append(teacher)

        return free
