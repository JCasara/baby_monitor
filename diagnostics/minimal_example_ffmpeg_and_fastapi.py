import subprocess

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get("/video_feed")
async def video_feed():
    # FFmpeg command to capture video from the camera at 1920x1080 and 30fps
    command = [
        'ffmpeg',
        '-f', 'v4l2',          # Use the Video4Linux2 input format (for Linux)
        '-framerate', '30',
        '-video_size', '648x480',
        '-i', '/dev/video0',   # Input device (change if necessary)
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-f', 'mpegts',
        'pipe:1'               # Output to stdout
    ]

    # Start the ffmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    async def stream_video():
        try:
            while True:
                # data = process.stdout.read(640*480*3)
                data = process.stdout.read(640*480*3)
                if not data:
                    break
                # yield data
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

        finally:
            process.stdout.close()
            process.stderr.close()
            process.terminate()

    return StreamingResponse(stream_video(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
