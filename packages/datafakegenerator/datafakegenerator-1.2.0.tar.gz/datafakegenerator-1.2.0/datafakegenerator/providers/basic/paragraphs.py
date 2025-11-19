import random
from lorem_text import lorem
from datafakegenerator.providers.base_provider import BaseProvider


class ParagraphsProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, min_paragraph: int = 1, max_paragraph: int = 10, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.min_paragraph = min_paragraph
        self.max_paragraph = max_paragraph

    def generate_non_blank(self, row_data=None):
        num_paragraphs = random.randint(self.min_paragraph, self.max_paragraph)
        paragraphs = [lorem.paragraph() for _ in range(num_paragraphs)]
        return "\n\n".join(paragraphs)
