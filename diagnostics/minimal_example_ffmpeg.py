from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import subprocess

app = FastAPI()

@app.get("/")
def index():
    return """
    <html>
    <body>
    <h1>Live Webcam Feed</h1>
    <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    """

@app.get("/video_feed")
def video_feed():
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-framerate', '30',
        '-video_size', '640x480',
        '-i', '/dev/video0',
        '-f', 'mjpeg',
        '-c:v', 'mjpeg',
        'pipe:1'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    def generate():
        while True:
            frame = process.stdout.read(1024)
            if not frame:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return StreamingResponse(generate(), media_type='multipart/x-mixed-replace; boundary=frame')
