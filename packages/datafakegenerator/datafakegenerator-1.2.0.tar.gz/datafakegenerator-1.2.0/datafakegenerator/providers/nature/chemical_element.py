from datafakegenerator.providers.base_provider import BaseProvider


class ChemicalElementProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['period_table'], **kwargs)

        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('period_table', 'symbol')

        symbol = row_data.get('chemical_symbol') if row_data else None

        return (
            self.lookup.get(symbol, {}).get('name')
            or self.get_row_data_from_datasets('period_table', 'name')
        )
