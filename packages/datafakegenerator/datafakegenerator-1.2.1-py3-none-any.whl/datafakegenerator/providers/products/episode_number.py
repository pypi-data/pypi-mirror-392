from datafakegenerator.providers.base_provider import BaseProvider
import random


class EpisodeNumberProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        season = random.randint(1, 10)
        episode = random.randint(1, 20)

        formats = [
            f"S{season:02d}E{episode:02d}",
            f"Episode {episode}",
            f"Season {season} Episode {episode}",
        ]

        return random.choice(formats)
