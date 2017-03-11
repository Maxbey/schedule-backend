from .models import Lesson


class ScheduleBuilder(object):
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

        sorted_by_ratio = sorted(with_ratio, key=lambda tup: tup[1])

        return [discipline[0] for discipline in sorted_by_ratio]

    def get_next_theme(self, discipline, troop):
        themes = discipline.themes.filter(term=troop.term).order_by('number')

        for theme in themes:
            if not Lesson.objects.filter(troop=troop, theme=theme).exists():
                return theme

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

    def is_audience_free(self, required_audience, lessons_in_same_time):
        return not lessons_in_same_time.filter(
            audiences__id__contains=required_audience.id
        ).exists()

    def find_free_audiences(self, theme, lessons_in_same_time):
        free = []

        for audience in theme.audiences.all():
            if self.is_audience_free(audience, lessons_in_same_time):
                free.append(audience)

        return free

    def is_teacher_free(self, required_teacher, lessons_in_same_time):
        return not lessons_in_same_time.filter(
            teachers__id__contains=required_teacher.id
        ).exists()

    def find_free_teachers(self, theme, lessons_in_same_time):
        free = []

        for teacher in theme.teachers.all():
            if self.is_teacher_free(teacher, lessons_in_same_time):
                free.append(teacher)

        return free
