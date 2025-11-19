from datafakegenerator.providers.base_provider import BaseProvider


class CssClassNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['css_class'], **kwargs)

    def generate_non_blank(self, row_data=None):
        return self.get_row_data_from_datasets('css_class', 'class')
