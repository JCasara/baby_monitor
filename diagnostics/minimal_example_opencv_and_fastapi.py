import time

import cv2
import face_recognition
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

# Initialize the video capture object (0 for the default webcam)
cap = cv2.VideoCapture(0)

# Set the camera frame rate and dimensions
frame_width = 640
frame_height = 480
frame_rate = 30  # Frames per second
FOURCC = 'YUYV'
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*FOURCC))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cap.set(cv2.CAP_PROP_FPS, frame_rate)

# User Controls
cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)                # Brightness
cap.set(cv2.CAP_PROP_CONTRAST, 32)                   # Contrast
cap.set(cv2.CAP_PROP_SATURATION, 64)                 # Saturation
cap.set(cv2.CAP_PROP_HUE, 0)                          # Hue
cap.set(cv2.CAP_PROP_AUTO_WB, 1)                     # White balance automatic (0 = off)
cap.set(cv2.CAP_PROP_GAMMA, 120)                      # Gamma
cap.set(cv2.CAP_PROP_GAIN, 4)                         # Gain
cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 4600)     # White balance temperature
cap.set(cv2.CAP_PROP_SHARPNESS, 2)                    # Sharpness
cap.set(cv2.CAP_PROP_BACKLIGHT, 0)                    # Backlight compensation
# cap.set(cv2.CAP_PROP_HW_ACCELERATION,0)

# Camera Controls
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)                # Auto exposure (1 = manual mode)
cap.set(cv2.CAP_PROP_EXPOSURE, 2500)                    # Exposure time absolute

print("Width:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("FPS (Set):", cap.get(cv2.CAP_PROP_FPS))
print("FOURCC:", cap.get(cv2.CAP_PROP_FOURCC))
print("FOURCC SETTING:", cv2.VideoWriter_fourcc(*FOURCC))

scale_factor = 0.25

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

        frame = cv2.flip(frame, 1)

        start_detection = time.time()
        # Perform face detections
        small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        # Get bbox for faces
        bbox = [(int(top / scale_factor), int(right / scale_factor), int(bottom / scale_factor), int(left / scale_factor)) for (top, right, bottom, left) in face_locations]

        # Draw bbox for faces on image
        for (top, right, bottom, left) in bbox:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        detection_time = time.time() - start_detection
        print(f"Detection time: {detection_time:.4f} seconds")


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
        print(f"Encoding time: {encoding_time:.4f} seconds")

        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
