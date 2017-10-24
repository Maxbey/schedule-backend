class VariationsBuilder(object):
    def __init__(self):
        self.schedule_variations = []
        self.calls = 0

    def build_variations_for_specialty(self, specialty, term):
        disciplines = specialty.disciplines

        self.build_schedule_variations([], disciplines, term)

        return self.schedule_variations

    def build_schedule_variations(self, current_variation, disciplines, term):
        theme_variations = self.get_theme_variations(
            current_variation, disciplines, term
        )
        self.calls += 1

        if not len(theme_variations):
            self.schedule_variations.append(current_variation)
            return

        for i in xrange(len(theme_variations)):
            current_copy = list(current_variation)

            theme = theme_variations.pop()
            current_copy.append(theme)
            self.build_schedule_variations(current_copy, disciplines, term)

    def get_theme_variations(self, current_variation, disciplines,
                             term):
        theme_variations = []

        for discipline in disciplines:
            theme_variations.append(
                self.get_next_theme(current_variation, discipline, term)
            )

        return [
            theme for theme in theme_variations
            if theme and self.check_prev_themes(current_variation, theme)
        ]

    def is_theme_passed(self, schedule_variation, theme):
        for passed_theme in schedule_variation:
            if passed_theme.id == theme.id:
                return True

        return False

    def get_next_theme(self, schedule_variation, discipline, term):
        themes = discipline.themes.filter(term=term)

        sorted_by_number = sorted(
            themes, key=lambda theme: float(theme.number)
        )

        for theme in sorted_by_number:
            if not self.is_theme_passed(schedule_variation, theme):
                return theme

        return None

    def check_prev_themes(self, schedule_variation, theme):
        if not theme.previous_themes.count():
            return True

        for previous_theme in theme.previous_themes.all():
            if not self.is_theme_passed(schedule_variation, previous_theme):
                return False

        return True
