from app.services.config_loader_service import ConfigLoaderService
from app.services.detection_service import DetectionService
from app.services.detector_service import DetectorService
from app.services.opencv_camera_service import \
    OpenCVCameraService as CameraService
# from app.services.ffmpeg_camera_service import \
#     FFmpegCameraService as CameraService
from app.services.pushover_service import PushoverService
from app.services.server_service import ServerService
from app.services.state_manager_service import StateManagerService
from app.services.stream_service import StreamService

if __name__ == "__main__":
    # Load the configuration using ConfigLoader
    config_loader = ConfigLoaderService()
    config = config_loader.load_config("config/config.yaml")

    # Initialize components
    camera_service = CameraService(config['video'])
    detection_service = DetectionService(config['video'].get('scale_factor', 0.5))
    pushover_service = PushoverService(api_token=config['pushover'].get('API_TOKEN'), user_key=config['pushover'].get('USER_KEY'))
    state_manager = StateManagerService(config=config, pushover_service=pushover_service)
    streamer = StreamService(camera_service=camera_service)
    detector = DetectorService(camera_service=camera_service, detection_service=detection_service, state_manager=state_manager) 
    server = ServerService(config=config, streamer=streamer, state_manager=state_manager)

    streamer.start()
    detector.start()

    try:
        server.run()
    finally:
        # pass
        detector.release_resources()
