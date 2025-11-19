# providers/advanced/character_sequence_provider.py
from datafakegenerator.providers.base_provider import BaseProvider


class MimeTypeProvider(BaseProvider):

    def __init__(self, *, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        key = self.get_random_data_by_list(list(self.it['mime_types'].keys()))
        return self.get_random_data_by_list(self.it['mime_types'][key])
