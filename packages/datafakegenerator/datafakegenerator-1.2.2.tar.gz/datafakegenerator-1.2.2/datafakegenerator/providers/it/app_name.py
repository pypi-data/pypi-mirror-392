from datafakegenerator.providers.base_provider import BaseProvider


class AppNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['app'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('app', 'app_bundle_id')

        app_bundle_id = row_data.get('app_bundle_id') if row_data else None

        return (
            self.lookup.get(app_bundle_id, {}).get('app_name')
            or self.get_row_data_from_datasets('app', 'app_name')
        )
