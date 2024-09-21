import asyncio
import time

import cv2

from app.services.config_loader_service import ConfigLoaderService
from app.services.detection_service import DetectionService
from app.services.opencv_camera import OpenCVCameraService
from app.utils.opencv_utils import draw_bboxes

# Grab config
config_loader = ConfigLoaderService()
config = config_loader.load_config('config/config.yaml')

camera_service = OpenCVCameraService(config['video'])
detection_service = DetectionService(scale_factor=config['video'].get('scale_factor', 0.25))

# Function to display the video feed
async def display_video():

    while True:
        frame = camera_service.capture_frame()

        pbbox, fbbox = await detection_service.run_detection(frame)
        # start_person_detection = time.time()
        # pbbox = await detection_service.detect_objects(frame, 'person')
        draw_bboxes(pbbox, frame)
        # person_detection = time.time() - start_person_detection
        # print(f"Person Detection time: {person_detection:.4f} seconds")

        # start_detection = time.time()
        # fbbox = await detection_service.detect_faces(frame)
        draw_bboxes(fbbox, frame)
        # detection_time = time.time() - start_detection
        # print(f"Face Detection time: {detection_time:.4f} seconds")

        # Show the frame in a window
        cv2.imshow("Video Feed", frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_service.release_resources()

if __name__ == "__main__":
    asyncio.run(display_video())
