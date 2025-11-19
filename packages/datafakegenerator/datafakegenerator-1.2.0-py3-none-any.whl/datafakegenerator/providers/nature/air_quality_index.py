from datafakegenerator.providers.base_provider import BaseProvider
import random


class AirQualityIndexProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):

        if row_data:
            ranges = {
                "Good": (0, 50),
                "Moderate": (51, 100),
                "Unhealthy for Sensitive Groups": (101, 150),
                "Unhealthy": (151, 200),
                "Very Unhealthy": (201, 300),
                "Hazardous": (301, 500)
            }

            if row_data:
                category = row_data.get('air_quality_category')
                if category in ranges:
                    return random.randint(*ranges[category])

        return random.randint(0, 500)
