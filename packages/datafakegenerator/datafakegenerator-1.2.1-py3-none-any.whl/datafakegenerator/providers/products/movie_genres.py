from datafakegenerator.providers.base_provider import BaseProvider


class MovieGenresProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['movies'], **kwargs)

        self.lookup = None

    def generate_non_blank(self, row_data=None):
        if self.lookup is None:
            self.lookup = self.get_dataset_lookup('movies', 'title')

        movie_title = row_data.get('movie_title') if row_data else None

        return (
            self.lookup.get(movie_title, {}).get('genres')
            or self.get_row_data_from_datasets('movies', 'genres')
        )
