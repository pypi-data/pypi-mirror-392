from datafakegenerator.providers.base_provider import BaseProvider
from providers.basic.duration import DurationProvider


class EngagementRecencyProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        return DurationProvider().generate_non_blank()
