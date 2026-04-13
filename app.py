import sys
import time
from pathlib import Path
from flask import Flask, Response, jsonify, render_template_string, request
import pyautogui
import mss

sys.path.insert(0, str(Path(__file__).parent / "src"))

from capture import ScreenCapture
from encoder import FrameEncoder

app = Flask(__name__)

encoder = FrameEncoder(quality=50, max_width=1280)
capture = ScreenCapture()

CLIENT_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Segunda tela</title>
  <style>
    body { margin: 0; background: #000; display: flex;
           justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }
    img  { max-width: 100%; max-height: 100vh; object-fit: contain; cursor: crosshair; }
  </style>
</head>
<body>
  <img id="stream" src="/stream" alt="stream">
  <script>
    const img = document.getElementById('stream');
    
    img.addEventListener('click', function(event) {
        const rect = img.getBoundingClientRect();
        
        // Calcula a posição do clique de forma proporcional (0.0 a 1.0)
        const percent_x = (event.clientX - rect.left) / rect.width;
        const percent_y = (event.clientY - rect.top) / rect.height;

        fetch('/api/input/click', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ px: percent_x, py: percent_y })
        });
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(CLIENT_HTML)

def generate_frames():
    while True:
        frame = capture.get_frame()
        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + frame +
                b"\r\n"
            )
        else:
            time.sleep(0.01)

@app.route("/stream")
def stream():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/api/monitors")
def monitors():
    return jsonify(capture.list_monitors())

@app.route("/api/input/click", methods=["POST"])
def handle_click():
    data = request.json
    px, py = data.get("px"), data.get("py")
    
    if px is not None and py is not None:
        with mss.mss() as sct:
            monitor = sct.monitors[capture.monitor_index]
            
            # Converte a proporção do front-end na coordenada absoluta do monitor
            target_x = int(monitor["left"] + (px * monitor["width"]))
            target_y = int(monitor["top"] + (py * monitor["height"]))
            
            pyautogui.click(x=target_x, y=target_y)
            
    return jsonify({"status": "success"})

if __name__ == "__main__":
    import socket

    capture.start(encoder)

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("\n  Segunda tela rodando em:")
    print(f"  -> http://localhost:5000")
    print(f"  -> http://{local_ip}:5000\n")

    app.run(host="0.0.0.0", port=5000, threaded=True)