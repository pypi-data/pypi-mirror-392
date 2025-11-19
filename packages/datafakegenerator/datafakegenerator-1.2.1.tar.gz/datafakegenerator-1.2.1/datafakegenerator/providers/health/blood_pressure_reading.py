from datafakegenerator.providers.base_provider import BaseProvider
import random


class BloodPressureReadingProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        systolic = random.randint(90, 160)
        diastolic = random.randint(60, min(100, systolic - 40))
        return f"{systolic}/{diastolic}"
