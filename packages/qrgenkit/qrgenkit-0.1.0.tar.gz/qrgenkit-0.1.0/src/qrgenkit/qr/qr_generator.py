import qrcode
from .qr_config import QrConfig

class QRGenerator:
    def __init__(self, config: QrConfig):
        self.config = config

    def generate_qr(self, data:str, output_file_path:str):
        qr = qrcode.QRCode(
            version=self.config.version,
            error_correction=self.config.error_correction,
            box_size=self.config.box_size,
            border=self.config.border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=self.config.fill_color, back_color=self.config.back_color)
        img.save(output_file_path)