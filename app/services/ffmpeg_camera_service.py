import select
import subprocess
import threading
from collections import deque
from typing import Any, Generator, Optional

import cv2
import numpy as np

from app.interfaces.camera_interface import CameraInterface


class FFmpegCameraService(CameraInterface):
    def __init__(self, video_config):
        self.scale_factor = video_config.get('scale_factor', 0.5)
        self.buffer_size = video_config.get('buffer_size', 10)
        self.frame_rate = video_config.get('frame_rate', 30)
        self.image_height = video_config.get('image_height', 480)
        self.image_width = video_config.get('image_width', 640)
        self.camera_device = '/dev/video0'
        self.frame_callback = None
        self.frame_buffer = deque(maxlen=self.buffer_size)
        self.running = True
        self.lock = threading.Lock()
        self.ffmpeg_process = self._start_ffmpeg_process()

    def _start_ffmpeg_process(self) -> subprocess.Popen:
        """
        Start the FFmpeg process to capture frames from the camera.

        Returns:
            subprocess.Popen: The FFmpeg subprocess for capturing frames.

        """
        # FFmpeg command to capture video from the camera at 1920x1080 and 30fps
        print("Starting ffmpeg command...")
        command = [
            'ffmpeg',
            '-f', 'v4l2',          # Use the Video4Linux2 input format (for Linux)
            '-framerate', f'{self.frame_rate}',
            '-video_size', f'{self.image_width}x{self.image_height}',
            '-i', f'{self.camera_device}',
            '-c:v', 'mpeg1video', # libx264 (previously)
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-f', 'mjpeg',
            'pipe:1'
        ]

        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def _capture_frame(self):
        """Capture camera frame using ffmpeg."""
        while self.running:
            if self.ffmpeg_process.stdout is None:
                raise RuntimeError("ffmpeg_process.stdout is None. Ensure the process is correctly initialized.")

            # raw_frame = self.ffmpeg_process.stdout.read(self.image_width * self.image_height * 3)
            raw_frame = self.ffmpeg_process.stdout.read()
            if not raw_frame:
                raise RuntimeError("Failed to capture frame via FFmpeg")

            if not raw_frame:
                return None

            frame = raw_frame
            # frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.image_height, self.image_width, 3))
            with self.lock:
                if frame is not None:
                    self.frame_buffer.append(frame)

    def generate_frames(self) -> Generator[Any, Any, Any]:
        """Generate a frame for the video server."""
        while self.running:
            frame = self.get_frame()
            if frame is None:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # ret, encoded_data = cv2.imencode('.jpg', frame)
            # if ret:
                # byte_data = encoded_data.tobytes()
                # yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + byte_data + b'\r\n')

    def set_frame_callback(self, callback):
        """Sets a callback function to indicate when the frame is ready."""
        self.frame_callback = callback

    def get_frame(self) -> Optional[np.ndarray]:
        """Get frame from frame_bufer."""
        with self.lock:
            if len(self.frame_buffer) > 0:
                return self.frame_buffer.popleft()

    def start(self) -> None:
        """Start stream thread."""
        self.thread = threading.Thread(target=self._capture_frame)
        self.thread.daemon = True
        self.thread.start()

    def release_resources(self) -> None:
        """Release ffmpeg resources."""
        self.running = False
        self.ffmpeg_process.terminate()
        self.thread.join()
        try:
            self.ffmpeg_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.ffmpeg_process.kill()
        finally:
            if self.ffmpeg_process.stdout is not None:
                self.ffmpeg_process.stdout.close()
