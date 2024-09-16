import threading
import time

import cv2

from .interfaces.camera_interface import CameraInterface
from .interfaces.detector_interface import DetectorInterface
from .interfaces.state_manager_interface import StateManagerInterface


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

    def _draw_bboxes(self, bbox_locations, frame):
        for (top, right, bottom, left) in bbox_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    def _draw_annotations(self, frame):
        state = self.state_manager.get_state()
        annotation_text = state.get_annotation()
        color = state.get_color()

        cv2.putText(frame, annotation_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    def _process_frame(self):
        while self.running:
            with self.lock:
                if len(self.camera_service.frame_buffer) > 0:
                    frame = self.camera_service.frame_buffer.popleft()
                else:
                    time.sleep(0.0333)
                    continue

                person_bboxes = self.detector_service.detect_persons(frame)
                if person_bboxes:
                    self._draw_bboxes(person_bboxes, frame)
                    face_bboxes = self.detector_service.detect_faces(frame)
                    if face_bboxes:
                        self._draw_bboxes(face_bboxes, frame)
                        self.state_manager.process_frame(True, True)
                    else:
                        self.state_manager.process_frame(True, False)
                else:
                    self.state_manager.process_frame(False, False)
                self._draw_annotations(frame)
                self.camera_service.frame_buffer.append(frame)
                        
    def start(self):
        self.thread = threading.Thread(target=self._process_frame)
        self.thread.daemon = True
        self.thread.start()

    def release_resources(self):
        self.running = False
        self.thread.join()
