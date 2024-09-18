import time

import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

# Initialize the video capture object (0 for the default webcam)
cap = cv2.VideoCapture(0)

# Set the camera frame rate and dimensions
frame_width = 1920
frame_height = 1080
frame_rate = 30  # Frames per second

cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cap.set(cv2.CAP_PROP_FPS, frame_rate)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

# print("Width:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# print("Height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print("FPS (Set):", cap.get(cv2.CAP_PROP_FPS))
# print("FOURCC:", cap.get(cv2.CAP_PROP_FOURCC))

def gen_frames():
    fps_frame_count = 0
    last_time = time.time()
    fps = 0
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Update FPS calculation
        fps_frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - last_time
        
        if elapsed_time > 1.0:
            fps = fps_frame_count / elapsed_time
            last_time = current_time
            fps_frame_count = 0
        
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
    uvicorn.run(app, host="0.0.0.0", port=8080)
