from datafakegenerator.providers.base_provider import BaseProvider


class StockSectorProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['stocks'], **kwargs)

    def generate_non_blank(self, row_data=None):
        stock_symbol = row_data.get('stock_symbol') if row_data else None
        stock_name = row_data.get('stock_name') if row_data else None

        if stock_symbol:
            return self.get_dataset_lookup('stocks', 'Symbol').get(stock_symbol, {}).get('Sector')

        if stock_name:
            return self.get_dataset_lookup('stocks', 'Name').get(stock_name, {}).get('Sector')

        return self.get_row_data_from_datasets('stocks', 'Sector')
