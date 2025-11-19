import time
import random
from datafakegenerator.providers.base_provider import BaseProvider


class MongodbObjectIdProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        timestamp = int(time.time())
        timestamp_hex = f"{timestamp:08x}"
        machine_pid_hex = ''.join(random.choices("0123456789abcdef", k=10))
        counter = random.randint(0, 0xFFFFFF)
        counter_hex = f"{counter:06x}"

        return f"{timestamp_hex}{machine_pid_hex}{counter_hex}"
