import threading
import time

import yaml

from app.video_face_detector import VideoFaceDetector
from app.video_stream_server import VideoStreamServer


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":

    config = load_config()
    # server_config = config["server"]
    video_config = config["video"]
    # threshold_config = config["threshold"]

    detector = VideoFaceDetector(scale_factor=video_config['scale_factor'],
                                 buffer_size=video_config['buffer_size'],
                                 frame_rate=video_config["frame_rate"])
    server = VideoStreamServer(face_detector=detector)

    # Start a thread for frame updating
    def update_frames():
        while detector.running:
            start_time = time.time()
            detector.update_frame()
            elapsed_time = time.time() - start_time
            sleep_time = max(0, detector.frame_interval - elapsed_time)
            time.sleep(sleep_time)

    frame_thread = threading.Thread(target=update_frames)
    frame_thread.daemon = True
    frame_thread.start()

    try:
        server.run()
    finally:
        detector.release_resources()
