from datafakegenerator.providers.base_provider import BaseProvider
import random


class TemperatureProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, type: str = "celcius", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.type = type

    def generate_non_blank(self, row_data=None):
        if self.type == "celsius":
            temp = round(random.uniform(-20.0, 45.0), 1)
            sign = "°C"
        elif self.type == "fahrenheit":
            temp = round(random.uniform(-4.0, 113.0), 1)
            sign = "°F"

        return f"{temp}{sign}"
