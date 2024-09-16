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
            '-f', 'v4l2',
            '-framerate', '30',
            '-video_size', '640x480',
            '-i', '/dev/video0',
            '-c:v', 'libx264',
            '-f', 'hls',
            '-hls_time', '2',
            '-hls_list_size', '10',
            '-hls_flags', 'delete_segments',
            '../static/stream.m3u8'
        ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    async def stream_video():
        try:
            while True:
                # data = process.stdout.read(640*480*3)
                data = process.stdout.read(640*480*3)
                if not data:
                    break
                yield data
                # yield (b'--frame\r\n'
                #     b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

        finally:
            process.stdout.close()
            process.stderr.close()
            process.terminate()

    return StreamingResponse(stream_video(), media_type='video/mpeg')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
