import asyncio
import threading
import time
from collections import deque

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.detection_interface import DetectionInterface
from app.interfaces.detector_interface import DetectorInterface
from app.interfaces.state_manager_interface import StateManagerInterface
from app.utils.opencv_utils import draw_annotations, draw_bboxes


class DetectorService(DetectorInterface):
    def __init__(self, camera_service: CameraInterface, detection_service: DetectionInterface, state_manager: StateManagerInterface):
        self.camera_service: CameraInterface = camera_service
        self.detection_service: DetectionInterface = detection_service
        self.state_manager: StateManagerInterface = state_manager
        self.running: bool = True
        self.fps: float = 0
        self.frame_count: int = 0
        self.start_time: float = time.time()
        self.condition = threading.Condition()
        self.frame_buffer = deque()
        self.lock = threading.Lock()

        self.camera_service.set_frame_callback(self.frame_available)
 
    def _process_frame(self) -> None:
        """Process frame by performing detections."""
        print("DetectorService: Processing Frame")
        while self.running:
            with self.condition:
                # Wait until notified of a new frame
                self.condition.wait()

            with self.camera_service.lock:
                frame = None
                if len(self.camera_service.frame_buffer) > 0:
                    frame = self.camera_service.frame_buffer.popleft()

            if frame is None or frame.size == 0:
                continue

            # with self.camera_service.lock:
            # person_bboxes = asyncio.run(self.detection_service.detect_persons(frame))
            # if person_bboxes:
            #     draw_bboxes(person_bboxes, frame)
            # else:
            #     self.state_manager.process_frame(False, False)
            face_bboxes = asyncio.run(self.detection_service.detect_faces(frame))
            if face_bboxes:
                draw_bboxes(face_bboxes, frame)
                self.state_manager.process_frame(True, True)
            else:
                self.state_manager.process_frame(True, False)

            draw_annotations(frame, self.state_manager.state)

            # Append processed frame back to frame_buffer
            with self.lock:
                self.frame_buffer.append(frame)

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
