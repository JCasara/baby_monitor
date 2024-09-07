from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import cv2
import time

app = FastAPI()

# Initialize the video capture object (0 for the default webcam)
cap = cv2.VideoCapture(0)

"""
Testing resolution 640x480
Supported Frame Rates at 640x480: [5, 7, 10, 15, 20, 24, 30]
Testing resolution 1280x720
Supported Frame Rates at 1280x720: [5, 7, 10]
Testing resolution 1920x1080
Supported Frame Rates at 1920x1080: [5]
"""

# Set the camera frame rate and dimensions
frame_width = 640
frame_height = 480
frame_rate = 30  # Frames per second

cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cap.set(cv2.CAP_PROP_FPS, frame_rate)

print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(cap.get(cv2.CAP_PROP_FPS))

def gen_frames():
    while True:
        start_time = time.time()
        success, frame = cap.read()
        if not success:
            break
        # Calculate FPS
        fps = 1.0 / (time.time() - start_time)
        # Put FPS on the frame
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

