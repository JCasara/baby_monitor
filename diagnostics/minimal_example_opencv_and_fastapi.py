import time

import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

# Initialize the video capture object (0 for the default webcam)
cap = cv2.VideoCapture(0)

# Set the camera frame rate and dimensions
frame_width = 640
frame_height = 480
frame_rate = 30  # Frames per second
FOURCC = 'MJPG'
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*FOURCC))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cap.set(cv2.CAP_PROP_FPS, frame_rate)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual exposure
cap.set(cv2.CAP_PROP_GAIN, 0)  # Fixed gain
cap.set(cv2.CAP_PROP_AUTO_WB, 0)  # Disable auto white balance
print("Width:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("FPS (Set):", cap.get(cv2.CAP_PROP_FPS))
print("FOURCC:", cap.get(cv2.CAP_PROP_FOURCC))
print("FOURCC SETTING:", cv2.VideoWriter_fourcc(*FOURCC))

def gen_frames():
    fps_frame_count = 0
    last_time = time.time()
    fps = 0
    while True:
        start_reading = time.time()
        success, frame = cap.read()
        read_time = time.time() - start_reading
        print(f"Read time: {read_time:.4f} seconds")
        if not success:
            break

        fps_frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - last_time
        
        if elapsed_time > 1.0:
            fps = fps_frame_count / elapsed_time
            last_time = current_time
            fps_frame_count = 0
        
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Measure encoding time
        start_encoding = time.time()
        _, buffer = cv2.imencode('.jpg', frame)
        encoding_time = time.time() - start_encoding
        # print(f"Encoding time: {encoding_time:.4f} seconds")

        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # Print or log encoding time if necessary
        # print(f"Encoding time: {encoding_time:.4f} seconds")

@app.get("/")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
