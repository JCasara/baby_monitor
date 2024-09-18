import asyncio
import threading
import time
from typing import List, Tuple

import cv2
import numpy as np

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.detection_interface import DetectionInterface
from app.interfaces.state_manager_interface import State, StateManagerInterface

GREEN: Tuple[int, int, int] = (0, 255, 0)
LINE_THICKNESS: int = 2
FONT_FACE: int = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE: int = 1

class DetectorService:
    def __init__(self, camera_service: CameraInterface, detection_service: DetectionInterface, state_manager: StateManagerInterface):
        self.camera_service: CameraInterface = camera_service
        self.detection_service: DetectionInterface = detection_service
        self.state_manager: StateManagerInterface = state_manager
        self.running: bool = True
        self.fps: float = 0
        self.frame_count: int = 0
        self.start_time: float = time.time()
        self.condition = threading.Condition()

        self.camera_service.set_frame_callback(self.frame_available)

    def _draw_bboxes(self, bbox_locations: List[Tuple[int, int, int, int]], frame: np.ndarray) -> None:
        """Draw bounding boxes for detections."""
        # Is there another way to draw the bboxes? Or can the bbox_locations be passed back to
        # the camera_service?
        for (top, right, bottom, left) in bbox_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), GREEN, LINE_THICKNESS)

    def _draw_annotations(self, frame) -> None:
        """Draw annotations on image that indicate state."""
        # Is there another way to draw the annotations? Or can the annotations be passed back to
        # the camera_service?
        ORG: Tuple[int, int] = (10, 50) # Bottom-left corner of the text string in the image

        state: State = self.state_manager.get_state()
        annotation_text: str = state.get_annotation()
        color: Tuple[int, int, int] = state.get_color()

        cv2.putText(frame, annotation_text, ORG, FONT_FACE, FONT_SCALE, color, LINE_THICKNESS)

    def _process_frame(self) -> None:
        """Process frame by performing detections."""
        while self.running:
            with self.condition:
                # Wait until notified of a new frame
                self.condition.wait()

            frame = self.camera_service.get_frame()

            if frame is None or frame.size == 0:
                continue

            with self.camera_service.lock:
                person_bboxes = asyncio.run(self.detection_service.detect_persons(frame))
                face_bboxes = asyncio.run(self.detection_service.detect_faces(frame))
                if person_bboxes:
                    self._draw_bboxes(person_bboxes, frame)
                    if face_bboxes:
                        self._draw_bboxes(face_bboxes, frame)
                        self.state_manager.process_frame(True, True)
                    else:
                        self.state_manager.process_frame(True, False)
                else:
                    self.state_manager.process_frame(False, False)

                self._draw_annotations(frame)

                # Append processed frame back to frame_buffer
                self.camera_service.frame_buffer.append(frame)
                        
    def frame_available(self):
        """Call this method when a new frame is added to the buffer."""
        with self.condition:
            self.condition.notify()  # Notify waiting threads

    def start(self) -> None:
        """Start video detector thread."""
        self.thread: threading.Thread = threading.Thread(target=self._process_frame)
        self.thread.daemon = True
        self.thread.start()

    def release_resources(self) -> None:
        """Release video detector resources."""
        self.running = False
        self.thread.join()
