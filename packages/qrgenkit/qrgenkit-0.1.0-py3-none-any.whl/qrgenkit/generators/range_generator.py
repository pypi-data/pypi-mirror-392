from .base_generator import BaseGenerator

from pathlib import Path

class RangeGenerator(BaseGenerator):
    def __init__(self, input_data: dict, generator, output_dir: str | Path, progress_callback=None):
        super().__init__(generator,output_dir,progress_callback)
        self.prefix = input_data.get('prefix','')
        self.suffix = input_data.get('suffix','')
        self.start = input_data['start']
        self.end = input_data['end']


    def _generate(self):
        for i in range(self.start, self.end+1):
            data = self.prefix + str(i) + self.suffix
            self._save_qr(data)
            if self.progress_callback:
                callback_data = {
                    'current_data': data,
                    'percent_complete': ((i - self.start + 1) / (self.end - self.start + 1)) * 100
                }
                self.progress_callback(callback_data)

