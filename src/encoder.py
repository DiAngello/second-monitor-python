import cv2
import numpy as np

class FrameEncoder:
    def __init__(self, quality=50, max_width=1280):
        self.quality = quality      
        self.max_width = max_width 

    def encode(self, img_bgra: np.ndarray) -> bytes:
        """Recebe array BGRA do mss, devolve bytes JPEG."""

        img_bgr = img_bgra[:, :, :3]

        # Reduz resolução se a tela for maior que max_width
        h, w = img_bgr.shape[:2]
        if w > self.max_width:
            scale = self.max_width / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            img_bgr = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

        success, buffer = cv2.imencode(
            ".jpg",
            img_bgr,
            [cv2.IMWRITE_JPEG_QUALITY, self.quality]
        )
        if not success:
            return b""

        return buffer.tobytes()