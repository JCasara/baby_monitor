import threading

import yaml

from app.video_face_detector import VideoFaceDetector
from app.video_stream_server import VideoStreamServer
from app.detection_state import StateManager


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":

    config = load_config()
    video_config = config["video"]
    pushover_config = config["pushover"]
    threshold_config = config["threshold"]

    state_manager = StateManager(threshold_config=threshold_config,pushover_config=pushover_config)
    detector = VideoFaceDetector(video_config=video_config, state_manager=state_manager) 
    server = VideoStreamServer(config=config, face_detector=detector)

    # Start a thread for frame updating
    def update_frames():
        while detector.running:
            detector.update_frame()

    frame_thread = threading.Thread(target=update_frames)
    frame_thread.daemon = True
    frame_thread.start()

    try:
        server.run()
    finally:
        detector.release_resources()
