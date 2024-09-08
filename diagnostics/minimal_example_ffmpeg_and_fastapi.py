from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import subprocess

app = FastAPI()

@app.get("/video_feed")
async def video_feed():
    # FFmpeg command to capture video from the camera at 1920x1080 and 30fps
    command = [
        'ffmpeg',
        '-f', 'v4l2',           # Linux video device input
        '-framerate', '30',      # Frame rate
        '-video_size', '1920x1080',  # Video resolution
        '-i', '/dev/video0',     # Camera device (adjust if necessary)
        '-vcodec', 'libx264',    # Encode video to H.264
        '-preset', 'ultrafast',  # FFmpeg encoding preset for low-latency
        '-tune', 'zerolatency',  # Tune for low-latency streaming
        '-f', 'mpegts',          # Output format
        'pipe:1'                      # Output to stdout
        '-an',
        '-y'
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stream_video():
        try:
            while True:
                data = process.stdout.read(1024)
                if not data:
                    break
                yield data
        finally:
            process.stdout.close()
            process.stderr.close()
            process.terminate()

    return StreamingResponse(stream_video(), media_type='/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

