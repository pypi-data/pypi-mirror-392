from datafakegenerator.providers.base_provider import BaseProvider
import random


class GradeLevelProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        num = random.randint(1, 12)
        suffix_grade = ['st', 'nd', 'rd', 'th']

        if num <= 3:
            return f"{num}{suffix_grade[num-1]} Grade"
        else:
            return f"{num}{suffix_grade[-1]} Grade"
