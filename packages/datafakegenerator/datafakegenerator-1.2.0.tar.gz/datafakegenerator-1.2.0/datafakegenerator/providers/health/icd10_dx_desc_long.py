from datafakegenerator.providers.base_provider import BaseProvider


class Icd10DxDescLongProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['ICD10_diagnosis'], **kwargs)

    def generate_non_blank(self, row_data=None):
        icd10_diagnosis_code = row_data.get(
            'icd10_diagnosis_code') if row_data else None
        icd10_dx_desc_short = row_data.get(
            'icd10_dx_desc_short') if row_data else None

        if icd10_diagnosis_code:
            return self.get_dataset_lookup('ICD10_diagnosis', 'ICD10_Diagnosis_Code').get(icd10_diagnosis_code, {}).get('ICD10_Dx_Desc_Long')

        if icd10_dx_desc_short:
            return self.get_dataset_lookup('ICD10_diagnosis', 'ICD10_Dx_Desc_Short').get(icd10_dx_desc_short, {}).get('ICD10_Dx_Desc_Long')

        return self.get_row_data_from_datasets('ICD10_diagnosis', 'ICD10_Dx_Desc_Long')
