from datafakegenerator.providers.base_provider import BaseProvider


class FileNameProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        category = self.get_random_data_by_list(list(self.file.keys()))
        extension = self.get_random_data_by_list(self.file[category])

        return f"{self.generate_username()}.{extension}"
