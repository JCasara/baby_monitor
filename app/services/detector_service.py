import numpy as np

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.detection_interface import DetectionInterface
from app.interfaces.detector_interface import DetectorInterface
from app.interfaces.state_manager_interface import StateManagerInterface
from app.utils.opencv_utils import display_fps, draw_annotations, draw_bboxes


class DetectorService(DetectorInterface):
    def __init__(self, camera_service: CameraInterface, detection_service: DetectionInterface, state_manager_service: StateManagerInterface):
        self.camera_service: CameraInterface = camera_service
        self.detection_service: DetectionInterface = detection_service
        self.state_manager_service: StateManagerInterface = state_manager_service
         
    async def process_frame(self) -> np.ndarray:
        """Process frame by performing detections."""
        frame = self.camera_service.capture_frame()

        person_bboxes, face_bboxes = await self.detection_service.run_detection(frame)
        if person_bboxes:
            draw_bboxes(person_bboxes, frame)
            if face_bboxes:
                draw_bboxes(face_bboxes, frame)
                self.state_manager_service.process_frame(True, True)
            else:
                self.state_manager_service.process_frame(True, False)
        else:
            self.state_manager_service.process_frame(False, False)

        draw_annotations(frame, self.state_manager_service.get_state())
        display_fps(frame, self.camera_service.fps)

        return frame
