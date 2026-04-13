import mss
import mss.tools
import threading
import time
import numpy as np

class ScreenCapture:
    def __init__(self):
        self._frame = None          # último frame capturado
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self.fps = 30
        self.monitor_index = 1      # 1 = monitor principal no mss

    def start(self, encoder):
        """Inicia o loop de captura em thread separada."""
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
        """Retorna o frame mais recente de forma thread-safe."""
        with self._lock:
            return self._frame

    def _capture_loop(self, encoder):
        interval = 1.0 / self.fps
        with mss.mss() as sct:
            while self._running:
                t0 = time.monotonic()

                # mss.monitors[0] = área total 
                # mss.monitors[1] = primeiro monitor, [2] = segundo
                monitor = sct.monitors[self.monitor_index]

                # grab() retorna um objeto ScreenShot com pixels em BGRA
                screenshot = sct.grab(monitor)

                img = np.array(screenshot)

                frame = encoder.encode(img)
                with self._lock:
                    self._frame = frame

                elapsed = time.monotonic() - t0
                sleep = interval - elapsed
                if sleep > 0:
                    time.sleep(sleep)

    def list_monitors(self):
        """Retorna lista de monitores disponíveis."""
        with mss.mss() as sct:
            return [
                {"index": i, "width": m["width"], "height": m["height"]}
                for i, m in enumerate(sct.monitors[1:], start=1)
            ]