from .base_generator import BaseGenerator
from pathlib import Path

class SingleGenerator(BaseGenerator):
    def __init__(self, input_data: str, generator, output_dir: str | Path,progress_callback=None):
        super().__init__(generator, output_dir,progress_callback)
        self.data = input_data

    def _generate(self):
        self._save_qr(self.data)
        if self.progress_callback:
            callback_data = {
                'current_data': self.data,
                'percent_complete': 100.0
            }
            self.progress_callback(callback_data)