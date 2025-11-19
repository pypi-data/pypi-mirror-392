import random
from lorem_text import lorem
from datafakegenerator.providers.base_provider import BaseProvider


class SentencesProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, min_sentence: int = 1, max_sentence: int = 10, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.min_sentence = min_sentence
        self.max_sentence = max_sentence

    def generate_non_blank(self, row_data=None):
        num_sentences = random.randint(self.min_sentence, self.max_sentence)
        sentences = [lorem.sentence() for _ in range(num_sentences)]
        text = " ".join(sentences)
        return f'"{text}"'
