import mss
import mss.tools
import threading
import time
import numpy as np
import pyautogui
import cv2

class ScreenCapture:
    def __init__(self):
        self._frame = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self.fps = 30
        self.monitor_index = 1

    def start(self, encoder):
        self._running = True
        self._thread = threading.Thread(
            target=self._capture_loop,
            args=(encoder,),
            daemon=True             
        )
        self._thread.start()

    def stop(self):
        self._running = False

    def get_frame(self):
        with self._lock:
            return self._frame

    def _capture_loop(self, encoder):
        interval = 1.0 / self.fps
        with mss.mss() as sct:
            while self._running:
                t0 = time.monotonic()
                monitor = sct.monitors[self.monitor_index]
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)

                # Desenha o cursor do host no frame capturado
                mx, my = pyautogui.position()
                rel_x = mx - monitor["left"]
                rel_y = my - monitor["top"]

                if 0 <= rel_x < monitor["width"] and 0 <= rel_y < monitor["height"]:
                    cv2.circle(img, (rel_x, rel_y), 6, (0, 0, 255), -1)
                    cv2.circle(img, (rel_x, rel_y), 6, (255, 255, 255), 2)

                frame = encoder.encode(img)
                with self._lock:
                    self._frame = frame

                elapsed = time.monotonic() - t0
                sleep = interval - elapsed
                if sleep > 0:
                    time.sleep(sleep)

    def list_monitors(self):
        with mss.mss() as sct:
            return [
                {"index": i, "width": m["width"], "height": m["height"]}
                for i, m in enumerate(sct.monitors[1:], start=1)
            ]