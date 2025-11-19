from datafakegenerator.providers.base_provider import BaseProvider


class HospitalNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['hospital'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('hospital', 'Hospital NPI')

        hospital_npi = row_data.get('hospital_npi') if row_data else None

        return (
            self.lookup.get(hospital_npi, {}).get('Hospital Name')
            or self.get_row_data_from_datasets('hospital', 'Hospital Name')
        )
