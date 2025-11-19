import random
import datetime
import platform
from datafakegenerator.providers.base_provider import BaseProvider


class DatetimeProvider(BaseProvider):
    def __init__(
        self,
        from_date: str = "01/01/1970",
        to_date: str = None,
        date_format: str = "mm/dd/yyyy",
        blank_percentage: float = 0.0,
        **kwargs
    ):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

        if to_date is None:
            to_date = datetime.date.today().strftime("%m/%d/%Y")
        self.from_date = self._parse_date(from_date)
        self.to_date = self._parse_date(to_date)
        self.format = date_format

        self.no_zero_day = "%#d" if platform.system() == "Windows" else "%-d"
        self.no_zero_month = "%#m" if platform.system() == "Windows" else "%-m"

    def _parse_date(self, date_str: str) -> datetime.datetime:
        return datetime.datetime.strptime(date_str, "%m/%d/%Y")

    def _random_datetime_between(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> datetime.datetime:
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + datetime.timedelta(seconds=random_seconds)

    def _format_datetime(self, dt: datetime.datetime) -> str:
        d, m = self.no_zero_day, self.no_zero_month
        format_map = {
            "m/d/yyyy": dt.strftime(f"{m}/{d}/%Y"),
            "mm/dd/yyyy": dt.strftime("%m/%d/%Y"),
            "yyyy-mm-dd": dt.strftime("%Y-%m-%d"),
            "yyyy-mm": dt.strftime("%Y-%m"),
            "d/m/yyyy": dt.strftime(f"{d}/{m}/%Y"),
            "dd/mm/yyyy": dt.strftime("%d/%m/%Y"),
            "d.m.yyyy": dt.strftime(f"{d}.{m}.%Y"),
            "dd.mm.yyyy": dt.strftime("%d.%m.%Y"),
            "dd-mm-yyyy": dt.strftime("%d-%m-%Y"),
            "dd-Mon-yyyy": dt.strftime("%d-%b-%Y"),
            "yyyy/mm/dd": dt.strftime("%Y/%m/%d"),
            "SQL datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "ISO 8601 (UTC)": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "epoch": str(int(dt.timestamp())),
            "unix timestamp": str(int(dt.timestamp())),
            "mongoDB epoch": str(int(dt.timestamp() * 1000)),
            "mongoDB ISO": dt.isoformat() + "Z",
        }

        return format_map.get(self.format, dt.isoformat())

    def generate_non_blank(self, row_data=None):
        random_datetime = self._random_datetime_between(
            self.from_date, self.to_date)
        return self._format_datetime(random_datetime)
