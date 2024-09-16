import threading
import time

import cv2

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.stream_interface import StreamInterface


class StreamService(StreamInterface):
    def __init__(self, camera_service: CameraInterface):
        self.camera_service = camera_service
        self.lock = threading.Lock()
        self.running = True
        self.frame_count = 0
        self.start_time = time.time()

    def _calculate_fps(self):
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time

    def _display_fps(self, frame):
        fps_text = f"FPS: {self.fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    def _update_frame(self):
        while self.running:
            frame = self.camera_service.capture_frame()
            if frame is not None:
                self._calculate_fps()
                self._display_fps(frame)
                with self.lock:
                    if len(self.camera_service.frame_buffer) > self.camera_service.buffer_size:  # Limit the buffer size
                        self.camera_service.frame_buffer.popleft()
                    self.camera_service.frame_buffer.append(frame)

    def start(self):
        self.thread = threading.Thread(target=self._update_frame)
        self.thread.daemon = True
        self.thread.start()

    def get_frame(self):
        with self.lock:
            if len(self.camera_service.frame_buffer) > 0:
                return self.camera_service.frame_buffer.popleft()
            return None

    def release_resources(self):
        self.running = False
        self.camera_service.release_resources()
        self.thread.join()
