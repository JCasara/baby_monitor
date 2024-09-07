from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import subprocess

app = FastAPI()

def generate_frames():
    # FFmpeg command to capture video and output MJPEG
    command = [
        'ffmpeg',
        '-f', 'v4l2',        # Use Video4Linux2
        '-framerate', '30',  # Frame rate
        '-video_size', '640x480',  # Resolution
        '-i', '/dev/video0', # Input device
        '-f', 'mjpeg',       # MJPEG format
        '-c:v', 'mjpeg',
        '-'
    ]
    
    # Start FFmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        while True:
            # Read chunks from FFmpeg output
            chunk = process.stdout.read(1024*1024)
            if not chunk:
                break
            # Yield MJPEG frames with proper boundary
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + chunk + b'\r\n')
    finally:
        process.stdout.close()
        process.stderr.close()
        process.terminate()

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
