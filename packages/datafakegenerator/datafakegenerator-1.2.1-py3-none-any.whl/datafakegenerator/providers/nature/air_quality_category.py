from datafakegenerator.providers.base_provider import BaseProvider


class AirQualityCategoryProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        if row_data:
            ranges = [
                (50, "Good"),
                (100, "Moderate"),
                (150, "Unhealthy for Sensitive Groups"),
                (200, "Unhealthy"),
                (300, "Very Unhealthy"),
                (500, "Hazardous")
            ]

            aqi = row_data.get('air_quality_index')
            if isinstance(aqi, (int, float)):
                for upper, category in ranges:
                    if aqi <= upper:
                        return category

        return self.get_random_data_by_list(self.nature['air_quality_category'])
