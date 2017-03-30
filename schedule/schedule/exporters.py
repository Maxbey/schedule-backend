# -*- coding: utf-8 -*-

import xlsxwriter


class ExcelExporter(object):
    headers = [
        u'Дата',
        u'Взвод',
        u'9:00 - 10:35',
        u'10:45 - 12:20',
        u'13:00 - 14:45'
    ]

    cells_for_lessons = ['C', 'D', 'E']

    @classmethod
    def export(cls, lessons_queryset):
        workbook = xlsxwriter.Workbook('exported.xlsx')
        worksheet = workbook.add_worksheet()

        cls.render_headers(worksheet)

        grouped_by_date = cls.group_lessons_by_date(lessons_queryset)
        grouped_by_troops = cls.group_lessons_by_troops(grouped_by_date)

        cls.render_data(workbook, worksheet, grouped_by_troops)
        workbook.close()

    @classmethod
    def render_data(cls, workbook, worksheet, grouped_by_troops):
        row = 1

        red_color = workbook.add_format()
        black_color = workbook.add_format()

        red_color.set_font_color('red')
        black_color.set_font_color('black')

        for group in grouped_by_troops:
            worksheet.write(row, 0, group[0].strftime('%d %m'))

            for troop in group[1]:
                worksheet.write(row, 1, troop[0])

                lesson_counter = 0
                for lesson in troop[1]:
                    current_format = black_color
                    lesson_str = cls.form_lesson_string(lesson)

                    if not len(lesson.teachers.all()) \
                            or not len(lesson.audiences.all()):
                        current_format = red_color

                    if lesson.theme.duration > 2:
                        range_template = '%s%i:%s%i'
                        end_cell = (
                            (lesson.theme.duration / 2) - (1 - lesson_counter)
                        )

                        lesson_range = range_template % (
                            cls.cells_for_lessons[lesson_counter],
                            row + 1,
                            cls.cells_for_lessons[end_cell],
                            row + 1
                        )
                        worksheet.merge_range(
                            lesson_range, lesson_str, current_format
                        )
                        lesson_counter += (lesson.theme.duration / 2)

                    else:
                        worksheet.write(
                            row, lesson_counter + 2, lesson_str,
                           current_format
                        )
                        lesson_counter += 1

                row += 1
            row += 1

    @classmethod
    def form_lesson_string(cls, lesson):
        template = '%s %s %s'

        a = u'%s Т №%s кл %s %s' % (
            lesson.theme.discipline.short_name,
            lesson.theme.number,
            cls.form_audiences_string(lesson.audiences.all()),
            cls.form_teachers_string(lesson.teachers.all())
        )

        return a

    @classmethod
    def form_teachers_string(cls, teachers):
        teachers_str = ''
        for teacher in teachers:
            teachers_str += teacher.name.split(' ')[0]
            teachers_str += ', '

        return teachers_str[:-2]

    @classmethod
    def form_audiences_string(cls, audiences):
        audiences_str = ''

        for audience in audiences:
            audiences_str += audience.location
            audiences_str += ', '

        return audiences_str[:-2]

    @classmethod
    def render_headers(cls, worksheet):
        column = 0

        for header in cls.headers:
            worksheet.write(0, column, header)
            column += 1

    @classmethod
    def group_lessons_by_date(cls, lessons_queryset):
        grouped = []
        dates_distinct = lessons_queryset.order_by('date_of').values(
            'date_of').distinct()
        for struct in dates_distinct:
            currect_date = struct['date_of']

            lessons_by_date = lessons_queryset.order_by('date_of').filter(
                date_of=currect_date
            )

            grouped.append((currect_date, list(lessons_by_date)))

        return grouped

    @classmethod
    def group_lessons_by_troops(cls, grouped_by_date):
        grouped = []

        for group in grouped_by_date:
            struct = (group[0], [])

            troop_codes_distinct = set(
                [lesson.troop.code for lesson in group[1]]
            )

            sorted_troop_codes = sorted(troop_codes_distinct)

            for code in sorted_troop_codes:
                troop_lessons = [
                    lesson for lesson in group[1] if lesson.troop.code == code
                    ]

                sorted_troop_lessons = sorted(
                    troop_lessons, key=lambda lesson: lesson.initial_hour
                )

                struct[1].append((code, sorted_troop_lessons))

            grouped.append(struct)

        return grouped
