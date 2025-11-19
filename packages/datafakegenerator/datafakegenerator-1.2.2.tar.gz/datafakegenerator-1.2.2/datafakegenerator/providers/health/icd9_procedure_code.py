from datafakegenerator.providers.base_provider import BaseProvider


class Icd9ProcedureCodeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['ICD9_procedure'], **kwargs)

    def generate_non_blank(self, row_data=None):
        return self.get_row_data_from_datasets('ICD9_procedure', 'IC9_PROCEDURE_CODE')
