import subprocess
from collections import deque

import numpy as np

from app.interfaces.camera_interface import CameraInterface


class FFmpegCameraService(CameraInterface):
    def __init__(self, video_config, camera_device='/dev/video0'):
        
        # TODO: replace with ffmpeg camera logic

        self.scale_factor = video_config.get('scale_factor')
        self.buffer_size = video_config.get('buffer_size')
        self.frame_rate = video_config.get('frame_rate')
        self.image_height = video_config.get('image_height')
        self.image_width = video_config.get('image_width')
        self.camera_device = camera_device
        self.frame_buffer = deque(maxlen=self.buffer_size)
        self.ffmpeg_process = self._start_ffmpeg_process()


    def _start_ffmpeg_process(self):
        """
        Start the FFmpeg process to capture frames from the camera.

        Returns:
            subprocess.Popen: The FFmpeg subprocess for capturing frames.

        """
        # FFmpeg command to capture video from the camera at 1920x1080 and 30fps
        command = [
            'ffmpeg',
            '-f', 'v4l2',
            '-framerate', f'{self.frame_rate}',      # Frame rate
            '-video_size', f'{self.image_width}x{self.image_height}',  # Video resolution
            '-i', f'{self.camera_device}',     # Camera device (adjust if necessary)
            '-f', 'mpegts',
            '-codec:v', 'mpeg1video',
            '-b:v', '800k',
            '-r', '30',
            '-'
        ]


        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


    def capture_frame(self) -> np.ndarray:
        raw_frame = self.ffmpeg_process.stdout.read(self.image_width * self.image_height * 3)
        if not raw_frame:
            raise RuntimeError("Failed to capture frame via FFmpeg")

        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.image_height, self.image_width, 3))
        if not frame.flags.writeable:
            frame = frame.copy()
        return frame

    def release_resources(self) -> None:
        self.ffmpeg_process.terminate()
        try:
            self.ffmpeg_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.ffmpeg_process.kill()
            self.ffmpeg_process.stdout.close()
