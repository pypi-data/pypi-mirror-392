import random
from datafakegenerator.providers.base_provider import BaseProvider


class DummyImageUrlProvider(BaseProvider):
    def __init__(
        self,
        blank_percentage: float = 0.0,
        min_w: int = 100,
        min_h: int = 100,
        max_w: int = 1000,
        max_h: int = 1000,
        **kwargs
    ):
        super().__init__(blank_percentage=blank_percentage, ** kwargs)
        self.min_w = min_w
        self.min_h = min_h
        self.max_w = max_w
        self.max_h = max_h
        self.bg_colors = self.get_row_data_from_datasets('colors', 'Hex')

    def generate_non_blank(self, row_data=None):
        w = random.randint(self.min_w, self.max_w)
        h = random.randint(self.min_h, self.max_h)
        text_color = self.get_random_data_by_list(['ffffff', '000000'])
        return f"http://dummyimage.com/{w}x{h}.png/{self.bg_colors.replace('#', '')}/{text_color}"
