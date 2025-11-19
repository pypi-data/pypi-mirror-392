from datafakegenerator.providers.base_provider import BaseProvider
import random
import datetime


class ModelVersionProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        pattern = self.get_random_data_by_list(
            ["semantic", "date", "calendar", "codename", "build", "experiment"])

        if pattern == "semantic":
            major = random.randint(1, 10)
            minor = random.randint(0, 30)
            patch = random.randint(0, 100)
            return f"v{major}.{minor}.{patch}"

        elif pattern == "date":
            start_date = datetime.date.today() - datetime.timedelta(days=5 * 365)
            rand_day = random.randint(0, 5 * 365)
            date_val = start_date + datetime.timedelta(days=rand_day)
            return f"model_{date_val.strftime('%Y_%m_%d')}"

        elif pattern == "calendar":
            year = random.randint(2020, 2025)
            month = random.randint(1, 12)
            return f"release_{year}.{month:02d}"

        elif pattern == "codename":
            names = ["phoenix", "eagle", "nebula",
                     "falcon", "atlas", "titan", "nova"]
            name = random.choice(names)
            version = random.randint(1, 10)
            minor = random.randint(0, 10)
            return f"{name}_v{version}.{minor}"

        elif pattern == "build":
            build_num = random.randint(100, 99999)
            return f"build-{build_num}"

        elif pattern == "experiment":
            run_id = random.randint(1, 999)
            suffix = random.choice(["a", "b", "c", "d", "e"])
            return f"exp_{run_id:03d}_{suffix}"
