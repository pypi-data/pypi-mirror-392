from datafakegenerator.providers.base_provider import BaseProvider


class StockNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['stocks'], **kwargs)
        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('stocks', 'Symbol')

        stock_symbol = row_data.get('stock_symbol') if row_data else None

        return (
            self.lookup.get(stock_symbol, {}).get('Name')
            or self.get_row_data_from_datasets('stocks', 'Name')
        )
