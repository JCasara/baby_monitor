import cv2
import face_recognition
import threading
import time
from flask import Flask, Response

class VideoFaceDetector:
    def __init__(self, scale_factor=0.5):
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")
        
        self.scale_factor = scale_factor
        self.output_frame = None
        self.lock = threading.Lock()
        self.running = True
        self.detection_thread = threading.Thread(target=self._run)
        self.detection_thread.start()
    
    def _resize_frame(self, frame):
        return cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
    
    def _detect_faces(self, rgb_frame):
        face_locations = face_recognition.face_locations(rgb_frame)
        return [(int(top / self.scale_factor), int(right / self.scale_factor),
                 int(bottom / self.scale_factor), int(left / self.scale_factor))
                for (top, right, bottom, left) in face_locations]
    
    def _draw_face_boxes(self, frame, face_locations):
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, 'Face', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    def _run(self):
        while self.running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Error: Failed to capture image.")
                continue
            
            small_frame = self._resize_frame(frame)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = self._detect_faces(rgb_small_frame)
            self._draw_face_boxes(frame, face_locations)
            
            with self.lock:
                self.output_frame = frame.copy()
    
    def get_frame(self):
        with self.lock:
            if self.output_frame is None:
                return None
            ret, encoded_image = cv2.imencode(".jpg", self.output_frame)
            if not ret:
                return None
            return encoded_image.tobytes()
    
    def stop(self):
        self.running = False
        self.video_capture.release()

class FlaskApp:
    def __init__(self, detector):
        self.detector = detector
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route("/video_feed")
        def video_feed():
            return Response(self.generate_stream(),
                            mimetype="multipart/x-mixed-replace; boundary=frame")
        
        @self.app.route("/")
        def index():
            return "Video feed available at /video_feed"
    
    def generate_stream(self):
        while self.detector.running:
            frame = self.detector.get_frame()
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def run(self, host="0.0.0.0", port=8080):
        try:
            self.app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
        except KeyboardInterrupt:
            self.detector.stop()

if __name__ == "__main__":
    detector = VideoFaceDetector(scale_factor=0.5)
    flask_app = FlaskApp(detector)
    flask_app.run()

