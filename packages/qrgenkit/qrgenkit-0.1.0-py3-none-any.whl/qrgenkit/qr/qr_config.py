import qrcode

class QrConfig:
    def __init__(self, box_size=10, border=1, fill_color="black", back_color="white"):
        self.version = 1
        self.error_correction = qrcode.constants.ERROR_CORRECT_H
        self.box_size = box_size
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color