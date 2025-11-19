from datafakegenerator.providers.base_provider import BaseProvider
import random


class BoardingGateProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        if random.choice([True, False]):
            gate_number = random.randint(1, 60)
            return f"Gate {gate_number}"
        else:
            letter = random.choice(["A", "B", "C", "D", "E"])
            number = random.randint(1, 50)
            return f"{letter}{number}"
