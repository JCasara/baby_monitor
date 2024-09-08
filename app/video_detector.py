import threading
import time

import cv2

from .interfaces.camera_interface import CameraInterface
from .interfaces.detector_interface import DetectorInterface
from .interfaces.state_manager_interface import StateManagerInterface
from .state_manager import DetectionState


class VideoDetector:
    def __init__(self, camera_service: CameraInterface, detector_service: DetectorInterface, state_manager: StateManagerInterface):
        self.camera_service = camera_service
        self.detector_service = detector_service
        self.state_manager = state_manager

        self.lock = threading.Lock()
        self.running = True
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()

    def update_frame(self):
        frame = self.camera_service.capture_frame()
        if frame is None:
            return

        person_bboxes = self.detector_service.detect_persons(frame)
        if person_bboxes:
            self._draw_bboxes(person_bboxes, frame)
            face_bboxes = self.detector_service.detect_faces(frame)
            if face_bboxes:
                self._draw_bboxes(face_bboxes, frame)
                self.state_manager.transition_state(True, True)
            else:
                self.state_manager.transition_state(True, False)
        else:
            self.state_manager.transition_state(False, False)

        self._draw_annotations(frame)
        self._calculate_fps()
        self._display_fps(frame)

        with self.lock:
            if self.running:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    self.camera_service.frame_buffer.append(buffer.tobytes())

    def _draw_bboxes(self, bbox_locations, frame):
        for (top, right, bottom, left) in bbox_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

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

    def _calculate_fps(self):
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time

    def _display_fps(self, frame):
        fps_text = f"FPS: {self.fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    def get_frame(self):
        with self.lock:
            if len(self.camera_service.frame_buffer) > 0:
                return self.camera_service.frame_buffer.popleft()
            return None

    def release_resources(self):
        self.running = False
        self.camera_service.release_resources()
