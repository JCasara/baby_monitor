from app.services.config_loader_service import ConfigLoaderService
from app.services.detection_service import DetectionService
from app.services.detector_service import DetectorService
from app.services.opencv_camera_service import \
    OpenCVCameraService as CameraService
from app.services.pushover_service import \
    PushoverService as NotificationService
from app.services.server_service import ServerService
from app.services.state_manager_service import StateManagerService

# Load Services
config_loader = ConfigLoaderService('config/config.yaml')
camera_service = CameraService(config_loader.config['video'])
detection_service = DetectionService(scale_factor=config_loader.config['video'].get('scale_factor', 0.25))
notification_service = NotificationService(api_token=config_loader.config['notification'].get('API_TOKEN'), user_key=config_loader.config['notification'].get('USER_KEY'))
state_manager_service = StateManagerService(config=config_loader.config, notification_service=notification_service)
detector_service = DetectorService(camera_service, detection_service, state_manager_service)
server_service = ServerService(config=config_loader.config, camera_service=camera_service, state_manager_service=state_manager_service, detector_service=detector_service)

if __name__ == "__main__":
    try:
        server_service.run()
    finally:
        print("Server shutdown.")
