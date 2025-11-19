from datafakegenerator.providers.base_provider import BaseProvider
from providers.basic.datetime import DatetimeProvider
import datetime
from dateutil.relativedelta import relativedelta


class PromoExpiryDateProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        current_date = datetime.datetime.now()
        future_date = current_date + relativedelta(years=5)
        formatted_current_date = current_date.strftime("%m/%d/%Y")
        formatted_future_date = future_date.strftime("%m/%d/%Y")
        dt = DatetimeProvider(from_date=formatted_current_date,
                              to_date=formatted_future_date)
        return dt.generate_non_blank()
