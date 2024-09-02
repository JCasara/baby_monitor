import cv2
import face_recognition
import threading
import time
from flask import Flask, Response
import numpy as np
from collections import deque

class VideoFaceDetector:
    def __init__(self, scale_factor=0.5, buffer_size=10, frame_rate=30):
        # Initialize the webcam
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")
        
        self.scale_factor = scale_factor
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.frame_buffer = deque(maxlen=buffer_size)  # Frame buffer
        self.lock = threading.Lock()
        self.running = True
        self.frame_rate = frame_rate
        self.frame_interval = 1.0 / frame_rate  # Calculate frame interval
        self.no_face_count = 0
        self.max_no_face_count = 100

    def _resize_frame(self, frame):
        """Resize the frame to improve processing speed."""
        return cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
    
    def _detect_faces(self, rgb_frame):
        """Detect faces in the frame using face_recognition."""
        face_locations = face_recognition.face_locations(rgb_frame)
        # Scale back bounding boxes to the original frame size
        return [(int(top / self.scale_factor), int(right / self.scale_factor),
                 int(bottom / self.scale_factor), int(left / self.scale_factor))
                for (top, right, bottom, left) in face_locations]
    
    def _calculate_fps(self):
        """Calculate and update the FPS."""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time
    
    def _draw_face_boxes(self, frame, face_locations):
        """Draw bounding boxes around detected faces."""
        if face_locations:
            self.no_face_count = 0
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, 'Face', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            self.no_face_count += 1
            if self.no_face_count >= self.max_no_face_count:
                cv2.putText(frame, 'Face not detected', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    def _display_fps(self, frame):
        """Display FPS on the frame."""
        fps_text = f"FPS: {self.fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    def update_frame(self):
        """Capture a frame from the webcam and process it."""
        ret, frame = self.video_capture.read()
        if not ret:
            print("Error: Failed to capture image.")
            return
        
        # Resize the frame
        small_frame = self._resize_frame(frame)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = self._detect_faces(rgb_small_frame)
        
        # Draw bounding boxes and FPS
        self._draw_face_boxes(frame, face_locations)
        self._calculate_fps()
        self._display_fps(frame)
        
        # Acquire a lock and set the output frame for streaming
        with self.lock:
            if self.running:
                # Encode frame and add to buffer
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    self.frame_buffer.append(buffer.tobytes())

    def get_frame(self):
        """Return the current frame from the buffer."""
        with self.lock:
            if len(self.frame_buffer) > 0:
                return self.frame_buffer.popleft()
            return None

    def release_resources(self):
        """Release video capture and close windows."""
        self.running = False
        self.video_capture.release()
        cv2.destroyAllWindows()

class VideoStreamServer:
    def __init__(self, face_detector):
        self.app = Flask(__name__)
        self.face_detector = face_detector
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
    
    def generate_frames(self):
        """Generate video frames for streaming."""
        while self.face_detector.running:
            frame = self.face_detector.get_frame()
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def video_feed(self):
        """Route to display the video stream."""
        return Response(self.generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    def run(self):
        """Run the Flask server."""
        self.app.run(host='0.0.0.0', port=8080, debug=False, threaded=True, use_reloader=False)

if __name__ == "__main__":
    frame_rate = 30  # Desired frame rate
    detector = VideoFaceDetector(scale_factor=0.5, buffer_size=10, frame_rate=frame_rate)
    server = VideoStreamServer(face_detector=detector)

    # Start a thread for frame updating
    def update_frames():
        while detector.running:
            start_time = time.time()
            detector.update_frame()
            elapsed_time = time.time() - start_time
            sleep_time = max(0, detector.frame_interval - elapsed_time)
            time.sleep(sleep_time)

    frame_thread = threading.Thread(target=update_frames)
    frame_thread.daemon = True
    frame_thread.start()

    try:
        server.run()
    finally:
        detector.release_resources()
