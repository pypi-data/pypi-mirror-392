from datafakegenerator.providers.base_provider import BaseProvider


class Icd9DxDescShortProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['ICD9_diagnosis'], **kwargs)

    def generate_non_blank(self, row_data=None):
        icd9_diagnosis_code = row_data.get(
            'icd9_diagnosis_code') if row_data else None

        icd9_dx_desc_long = row_data.get(
            'icd9_dx_desc_long') if row_data else None

        if icd9_diagnosis_code:
            return self.get_dataset_lookup('ICD9_diagnosis', 'IC9_DIAGNOSIS_CODE').get(icd9_diagnosis_code, {}).get('IC9_DX_DESC_LONG')

        if icd9_dx_desc_long:
            return self.get_dataset_lookup('ICD9_diagnosis', 'IC9_DX_DESC_LONG').get(icd9_dx_desc_long, {}).get('IC9_DIAGNOSIS_CODE')

        return self.get_row_data_from_datasets('ICD9_diagnosis', 'IC9_DX_DESC_SHORT')
