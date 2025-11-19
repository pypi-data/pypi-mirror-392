from datafakegenerator.providers.base_provider import BaseProvider


class LanguageCodeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['language'], **kwargs)

        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('language', 'name')

        name = row_data.get('language') if row_data else None

        return (
            self.lookup.get(name, {}).get('code')
            or self.get_row_data_from_datasets('language', 'code')
        )
