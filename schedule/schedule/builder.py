from datetime import timedelta
from random import shuffle

from django.conf import settings
from django.core.cache import cache

from .models import Lesson, Troop


class ScheduleBuilder(object):
    def build(self, date, term_length):
        self_ed_themes_buffer = {}
        for i in range(term_length):
            troop_list = list(Troop.objects.all())
            shuffle(troop_list)

            for troop in troop_list:
                date = date - timedelta(days=date.weekday())
                date = date + timedelta(days=troop.day)
                hours = 0
                themes_today = []

                while hours != settings.LESSON_HOURS:
                    disciplines = self.get_disciplines_by_priority(troop)

                    lesson_dependencies = self.find_lesson_dependencies(
                        disciplines, troop, date, hours
                    )

                    if lesson_dependencies is None:
                        break

                    theme, teachers, audiences = lesson_dependencies
                    themes_today.append(theme)

                    self.create_lesson(
                        date, troop, hours,
                        theme, teachers, audiences, theme.duration
                    )

                    hours += theme.duration

                if not str(troop.id) in self_ed_themes_buffer:
                    self_ed_themes_buffer[str(troop.id)] = []

                self_eds_today = self.sort_themes_with_self_ed(themes_today)
                self_eds_buffer = self.sort_themes_with_self_ed(
                    self_ed_themes_buffer[str(troop.id)]
                )

                self_ed_themes_buffer[str(troop.id)] = self_eds_today \
                                                       + self_eds_buffer

                while hours != settings.LESSON_HOURS + \
                        settings.SELF_EDUCATION_HOURS:
                    lesson_dependencies = self.find_self_ed_dependencies(
                        self_ed_themes_buffer[str(troop.id)][:],
                        troop, date, hours
                    )

                    if lesson_dependencies is None:
                        break

                    theme, teachers, audiences = lesson_dependencies

                    self.create_lesson(
                        date, troop, hours, theme,
                        teachers, audiences, theme.self_education_hours, True
                    )

                    hours += theme.self_education_hours

                    self.remove_item_by_id(
                        self_ed_themes_buffer[str(troop.id)],
                        theme.id
                    )

            date = date + timedelta(weeks=1)

    def remove_item_by_id(self, items, id):
        for index, item in enumerate(items):
            if item.id == id:
                del items[index]
                break

    def create_lesson(self, date_of, troop, initial_hour,
                      theme, teachers, audiences, delta, self_ed=False):
        lesson = Lesson.objects.create(
            date_of=date_of, initial_hour=initial_hour,
            troop=troop, theme=theme, self_education=self_ed
        )

        lesson.teachers.set(teachers)
        lesson.audiences.set(audiences)

        cache.set(
            'current_term_load',
            int(cache.get('current_term_load')) + delta,
            timeout=None
        )

        return lesson

    def sort_themes_with_self_ed(self, themes):
        with_self_ed = [
            theme for theme in themes
            if theme.self_education_hours
        ]

        return sorted(
            with_self_ed, key=lambda theme: theme.self_education_hours,
            reverse=True
        )

    def find_self_ed_dependencies(
            self, themes, troop, date, initial_hour):
        max_end_hour = settings.LESSON_HOURS + \
                       settings.SELF_EDUCATION_HOURS
        themes = [
            theme for theme in themes
            if not initial_hour + theme.self_education_hours > max_end_hour
        ]

        while True:
            if not len(themes):
                return None

            theme = themes[0]

            lessons_in_same_time = self.get_lessons_in_same_time(
                theme, troop, date, initial_hour
            )

            found_teachers = self.find_free_teachers(
                theme, lessons_in_same_time
            )

            if not len(found_teachers):
                if len(themes) > 1:
                    themes.pop(0)
                    continue

                found_teachers = []

            found_audiences = self.find_free_audiences(
                theme, lessons_in_same_time
            )

            if not len(found_audiences):
                if len(themes) > 1:
                    themes.pop(0)
                    continue

                found_audiences = []

            if not len(found_teachers):
                teachers = []
            else:
                teachers = [self.sort_teachers_by_priority(found_teachers)[0]]

            if not len(found_audiences):
                audiences = []
            else:
                audiences = [found_audiences[0]]

            return theme, teachers, audiences

    def find_lesson_dependencies(self, disciplines, troop,
                                 date, initial_hour):
        if disciplines[0][1] == 1:
            return None

        themes = self.fetch_disciplines_head_themes(
            troop, initial_hour, disciplines
        )

        while True:
            if not len(themes):
                return None

            theme = themes[0]

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
                teachers = self.sort_teachers_by_priority(
                    found_teachers
                )[0:theme.teachers_count]
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
            if not (theme.duration + initial_hour > settings.LESSON_HOURS)
            and self.check_prev_themes(theme, troop)
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

            for theme in discipline.themes.filter(term=troop.term):
                if Lesson.objects.filter(
                        troop=troop, theme=theme, self_education=False
                ).exists():
                    hours += theme.duration

                if Lesson.objects.filter(
                        troop=troop, theme=theme, self_education=True
                ).exists():
                    hours += theme.self_education_hours

            course_length = discipline.calc_course_length(
                troop.term, troop.specialty
            )
            if not course_length:
                continue

            with_ratio.append(
                (discipline, float(hours) / float(course_length))
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
