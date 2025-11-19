from datafakegenerator.providers.base_provider import BaseProvider


class HospitalStreetAddressProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['hospital'], **kwargs)

    def generate_non_blank(self, row_data=None):
        hospital_npi = row_data.get('hospital_npi') if row_data else None

        if hospital_npi:
            return self.get_dataset_lookup('hospital', 'Hospital NPI').get(hospital_npi, {}).get('Hospital Street Address')

        return self.get_row_data_from_datasets('hospital', 'Hospital Street Address')
