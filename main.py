import threading

from app.services.config_loader_service import ConfigLoader
from app.services.detector_service import DetectorService
from app.services.opencv_camera_service import \
    OpenCVCameraService as CameraService
# from app.services.ffmpeg_camera_service import \
#     FFmpegCameraService as CameraService
from app.services.pushover_service import PushoverService
from app.state_manager import StateManager
from app.video_detector import VideoDetector
from app.video_stream_server import VideoStreamServer


def signal_handler(sig, frame):
    print('Signal received, shutting down...')
    detector.running = False  # Stop the frame updating thread
    detector.release_resources()
    sys.exit(0)

if __name__ == "__main__":
    # Load the configuration using ConfigLoader
    config_loader = ConfigLoader()
    config = config_loader.load_config("config/config.yaml")

    # Initialize components
    camera_service = CameraService(config['video'])
    detector_service = DetectorService(config['video'].get('scale_factor', 0.5))
    pushover_service = PushoverService(api_token=config['pushover'].get('API_TOKEN'), user_key=config['pushover'].get('USER_KEY'))
    state_manager = StateManager(config=config, pushover_service=pushover_service)
    detector = VideoDetector(camera_service=camera_service, detector_service=detector_service, state_manager=state_manager) 
    server = VideoStreamServer(config=config, face_detector=detector, state_manager=state_manager)

    # Start a thread for frame updating
    def update_frames():
        while detector.running:
            detector.update_frame()
        print("Frame updating stopped.")

    def make_detections():
        while detector.running:
            if detector.frame_count % camera_service.frame_rate == 0:
                detector.make_detections()
        print("Detections stopped.")


    frame_thread = threading.Thread(target=update_frames)
    frame_thread.daemon = True
    frame_thread.start()

    detection_thread = threading.Thread(target=make_detections)
    detection_thread.daemon = True
    detection_thread.start()

    try:
        server.run()
    finally:
        detector.release_resources()
