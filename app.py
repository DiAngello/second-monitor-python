import sys
import time
from pathlib import Path
from flask import Flask, Response, jsonify, render_template_string

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
           justify-content: center; align-items: center; min-height: 100vh; }
    img  { max-width: 100%; max-height: 100vh; object-fit: contain; }
  </style>
</head>
<body>
  <img src="/stream" alt="stream">
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(CLIENT_HTML)

def generate_frames():
    """
    Gerador que produz frames no formato MJPEG.
    
    Formato MJPEG:
      --frame\\r\\n
      Content-Type: image/jpeg\\r\\n
      \\r\\n
      <bytes do JPEG>
      \\r\\n
    """
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

if __name__ == "__main__":
    import socket

    # Inicia captura antes do servidor
    capture.start(encoder)

    # Descobre o IP local para exibir no terminal
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("\n  Segunda tela rodando em:")
    print(f"  -> http://localhost:5000")
    print(f"  -> http://{local_ip}:5000\n")
    print("  No outro PC, abra o navegador e acesse o IP acima.\n")

    app.run(host="0.0.0.0", port=5000, threaded=True)