import threading
import time
from collections import deque

import cv2
import face_recognition
import torch

from app.detection_state import DetectionState


class VideoFaceDetector:
    def __init__(self, video_config, state_manager):
        # Initialize the webcam
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")
        
        self.scale_factor = video_config.get('scale_factor')
        self.buffer_size = video_config.get('buffer_size')
        self.frame_rate = video_config.get("frame_rate")
        self.frame_buffer = deque(maxlen=self.buffer_size)  # Frame buffer
        self.lock = threading.Lock()
        self.running = True
        self.frame_interval = 1.0 / self.frame_rate  # Calculate frame interval
        self.state_manager = state_manager
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.detection_interval = 100
        self.detection_counter = 0
        self.last_person_detected = False

    def _resize_frame(self, frame):
        """Resize the frame to improve processing speed."""
        return cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)

    def _scale_bbox(self, top, right, bottom, left):
        """Scale back bounding boxes to the original frame size"""
        return (int(top / self.scale_factor), int(right / self.scale_factor),
                 int(bottom / self.scale_factor), int(left / self.scale_factor))

    def _get_bbox_persons(self, person_locations):
        """Detect person in the frame using yolo."""
        person_bboxes = []
        for _, row in person_locations.iterrows():
            left, top, right, bottom = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            person_bboxes.append((top, right, bottom, left))
        return [self._scale_bbox(top, right, bottom, left)
                for (top, right, bottom, left) in person_bboxes]

    def _get_bbox_faces(self, face_locations):
        """Detect faces in the frame using face_recognition."""
        return [self._scale_bbox(top, right, bottom, left)
                for (top, right, bottom, left) in face_locations]

    def _calculate_fps(self):
        """Calculate and update the FPS."""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time

    def _draw_annotations(self, frame):
        """Draw the appropriate annotations based on the current state."""
        # if self.state_manager.get_state() == DetectionState.FACE_DETECTED:
        #     annotation_text = "Face"
        #     color = (0, 255, 0)
        # elif self.state_manager.get_state() == DetectionState.NO_FACE_DETECTED:
        #     annotation_text = "Face Not Detected"
        #     color = (0, 0, 255)
        # elif self.state_manager.get_state() == DetectionState.PERSON_DETECTED:
        annotation_text = "Person"
        color = (255, 0, 0)
        # else:
        #     annotation_text = "Idle"
        #     color = (255, 255, 255)

        cv2.putText(frame, annotation_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    def _draw_bboxes(self, bbox_locations, frame):
        for (top, right, bottom, left) in bbox_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    def update_frame(self):
        """Capture a frame from the webcam and process it."""
        ret, frame = self.video_capture.read()
        if not ret:
            print("Error: Failed to capture image.")
            return
        
        # Resize the frame
        small_frame = self._resize_frame(frame)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect persons
        # if self.detection_counter == 0:
        # yolo_results = self.yolo_model(rgb_small_frame)
        # yolo_locations = yolo_results.pandas().xyxy[0]
        # person_locations = yolo_locations[yolo_locations['name'] == 'person']
        #
        # # get bboxes for persons
        # bbox_persons = self._get_bbox_persons(person_locations)
        #
        # # self.last_person_detected = len(person_locations) > 0
        # # person_detected = self.last_person_detected
        # person_detected = len(person_locations) > 0
        #
        # # Draw person boxes if in PERSON_DETECTED state
        # if person_detected:
        #     self._draw_bboxes(bbox_persons, frame)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)

        # get bboxes for faces
        bbox_faces = self._get_bbox_faces(face_locations)

        # Handle state transitions
        face_detected = len(bbox_faces) > 0
        # self.state_manager.transition_state(person_detected, face_detected)

        # Draw face boxes if in FACE_DETECTED state
        if face_detected:
            self._draw_bboxes(bbox_faces, frame)
           
        
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
