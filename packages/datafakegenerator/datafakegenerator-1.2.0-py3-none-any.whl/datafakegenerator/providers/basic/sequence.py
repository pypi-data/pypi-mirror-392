import random
from datafakegenerator.providers.base_provider import BaseProvider


class SequenceProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, start_at: int = 1, step: int = 1, repeat: int = 1, restart_at: int = None, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.start_at = start_at
        self.step = step
        self.repeat = repeat
        self.restart_at = restart_at
        self.current_value = start_at
        self.repeat_count = 0

    def generate_non_blank(self, row_data=None):
        value = self.current_value
        self.repeat_count += 1

        # When the current value has been repeated enough times, move forward
        if self.repeat_count >= self.repeat:
            self.current_value += self.step
            self.repeat_count = 0

            # If restart is enabled and threshold reached, reset
            if self.restart_at is not None and self.current_value > self.restart_at:
                self.current_value = self.start_at

        return value
