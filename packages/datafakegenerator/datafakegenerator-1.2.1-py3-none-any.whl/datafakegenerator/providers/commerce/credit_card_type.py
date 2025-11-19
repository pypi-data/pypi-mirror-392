from datafakegenerator.providers.base_provider import BaseProvider


class CreditCardTypeProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.credit_card_provider = [
            "Visa",
            "MasterCard",
            "American Express",
            "Discover",
            "JCB",
            "Diners Club",
            "UnionPay"
        ]

    def generate_non_blank(self, row_data=None):
        return self.get_random_data_by_list(self.credit_card_provider)
