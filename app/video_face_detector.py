import threading
import time
from collections import deque

import cv2
import face_recognition
import torch

from app.detection_state import DetectionState, StateManager


class VideoFaceDetector:
    def __init__(self, pushover_config, scale_factor=1.0, buffer_size=1000, frame_rate=30):
        # Initialize the webcam
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")
        
        self.scale_factor = scale_factor
        self.frame_buffer = deque(maxlen=buffer_size)  # Frame buffer
        self.lock = threading.Lock()
        self.running = True
        self.frame_rate = frame_rate
        self.frame_interval = 1.0 / frame_rate  # Calculate frame interval
        self.state_manager = StateManager(pushover_config=pushover_config)
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.person_model = model = torch.hub.load('ultralytics/yolov5', 'yolov5n')
        self.detection_interval = 100
        self.detection_counter = 0
        self.last_person_detected = False

    def _resize_frame(self, frame):
        """Resize the frame to improve processing speed."""
        return cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
    
    def _detect_person(self, person_detections):
        """Detect person in the frame using yolo."""
        for _, row in person_detections.iterrows():
            left, top, right, bottom = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        # Scale back bounding boxes to the original frame size
        return (int(top / self.scale_factor), int(right / self.scale_factor),
                 int(bottom / self.scale_factor), int(left / self.scale_factor))

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

    def _draw_annotations(self, frame):
        """Draw the appropriate annotations based on the current state."""
        if self.state_manager.get_state() == DetectionState.FACE_DETECTED:
            annotation_text = "Face"
            color = (0, 255, 0)
        elif self.state_manager.get_state() == DetectionState.NO_FACE_DETECTED:
            annotation_text = "Face Not Detected"
            color = (0, 0, 255)
        elif self.state_manager.get_state() == DetectionState.PERSON_DETECTED:
            annotation_text = "Person"
            color = (255, 0, 0)
        else:
            annotation_text = "Idle"
            color = (255, 255, 255)

        cv2.putText(frame, annotation_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    def update_frame(self):
        """Capture a frame from the webcam and process it."""
        ret, frame = self.video_capture.read()
        if not ret:
            print("Error: Failed to capture image.")
            return
        
        # Resize the frame
        small_frame = self._resize_frame(frame)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect person
        if self.detection_counter == 0:
            person_results = self.person_model(rgb_small_frame)
            person_detections = person_results.pandas().xyxy[0]
            person_detections = person_detections[person_detections['name'] == 'person']
            self.last_person_detected = len(person_detections) > 0
        person_detected = self.last_person_detected

        # Detect faces
        face_locations = self._detect_faces(rgb_small_frame)
        
        # Handle state transitions
        face_detected = len(face_locations) > 0
        self.state_manager.transition_state(person_detected, face_detected)
        
        # Draw face boxes if in FACE_DETECTED state
        if face_detected:
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Draw the appropriate annotations
        self._draw_annotations(frame)
        
        # Calculate FPS and display it
        self._calculate_fps()
        self._display_fps(frame)
        
        # Acquire a lock and set the output frame for streaming
        with self.lock:
            if self.running:
                # Encode frame and add to buffer
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    self.frame_buffer.append(buffer.tobytes())

        # Update the detection counter
        self.detection_counter = (self.detection_counter + 1) % self.detection_interval

    def _display_fps(self, frame):
        """Display FPS on the frame."""
        fps_text = f"FPS: {self.fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
 
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
