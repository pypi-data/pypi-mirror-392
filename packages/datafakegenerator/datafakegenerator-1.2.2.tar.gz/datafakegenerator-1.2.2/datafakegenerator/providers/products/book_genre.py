from datafakegenerator.providers.base_provider import BaseProvider
import ast


class BookGenreProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['books'], **kwargs)

    def generate_non_blank(self, row_data=None):
        genres_list = ast.literal_eval(
            self.get_row_data_from_datasets('books', "genres"))

        return self.get_random_data_by_list(genres_list)
