from datafakegenerator.providers.base_provider import BaseProvider
import random


class LatencyProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)

    def generate_non_blank(self, row_data=None):
        network_type = None
        if row_data:
            network_type = row_data.get('network_type')
            min_latency, max_latency = self.communication['latency_range'].get(
                network_type)
        else:
            network_type = self.get_random_data_by_list(
                list(self.communication['latency_range'].keys()))
            min_latency, max_latency = self.communication['latency_range'].get(
                network_type)

        return f"{random.randint(min_latency, max_latency)}ms"
