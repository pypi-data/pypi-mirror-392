from datafakegenerator.providers.base_provider import BaseProvider
import random
import string


class ClassroomNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, format: str = "Auto", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.format = format

    def generate_non_blank(self, row_data=None):
        formats = {
            "Room": f"Room {random.randint(1, 999)}",
            "Lab": f"Lab {random.randint(1, 50)}{random.choice(string.ascii_uppercase)}",
            "Lecture": f"Lecture Hall {random.choice(string.ascii_uppercase)}",
        }

        if self.format == "Auto":
            return random.choice(list(formats.values()))

        if self.format in formats:
            return formats[self.format]

        return f"Room {random.randint(1, 999)}"
