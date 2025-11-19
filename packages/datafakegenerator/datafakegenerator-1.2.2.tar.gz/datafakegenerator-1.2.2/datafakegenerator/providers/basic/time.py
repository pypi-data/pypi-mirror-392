import random
from datetime import datetime, timedelta
from datafakegenerator.providers.base_provider import BaseProvider


class TimeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, time_from="00:00", time_to="23:59", fmt="24 Hour", **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.time_from = time_from
        self.time_to = time_to
        self.fmt = fmt

    def generate_non_blank(self, row_data=None):
        fmt_base = "%H:%M"
        t1 = datetime.strptime(self.time_from, fmt_base)
        t2 = datetime.strptime(self.time_to, fmt_base)

        delta = (t2 - t1).seconds
        random_seconds = random.randint(0, delta)
        random_time = (t1 + timedelta(seconds=random_seconds))

        if self.fmt == "24 Hour":
            return random_time.strftime("%H:%M")
        elif self.fmt == "24 Hour w/seconds":
            return random_time.strftime("%H:%M:%S")
        elif self.fmt == "24 Hour w/millis":
            return random_time.strftime("%H:%M:%S.") + f"{random_time.microsecond // 1000:03d}"
        elif self.fmt == "12 Hour":
            return random_time.strftime("%I:%M %p")
        elif self.fmt == "12 Hour w/seconds":
            return random_time.strftime("%I:%M:%S %p")
        elif self.fmt == "12 Hour w/millis":
            return random_time.strftime("%I:%M:%S.") + f"{random_time.microsecond // 1000:03d} " + random_time.strftime("%p")
        else:
            raise ValueError(f"Unknown format: {self.fmt}")
