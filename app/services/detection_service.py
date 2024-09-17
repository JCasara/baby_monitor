from typing import List, Tuple

import cv2
import face_recognition
import torch

from app.interfaces.detection_interface import DetectionInterface


class DetectionService(DetectionInterface):
    def __init__(self, scale_factor):
        self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.scale_factor = scale_factor

    def _scale_bbox(self, top, right, bottom, left) -> Tuple[int, int, int, int]:
        return (int(top / self.scale_factor), int(right / self.scale_factor),
                int(bottom / self.scale_factor), int(left / self.scale_factor))
    
    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        return [self._scale_bbox(top, right, bottom, left) for (top, right, bottom, left) in face_locations]

    def detect_persons(self, frame) -> List[Tuple[int, int, int, int]]:
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        yolo_results = self.yolo_model(small_frame)
        yolo_locations = yolo_results.pandas().xyxy[0]
        person_locations = yolo_locations[yolo_locations['name'] == 'person']
        return [self._scale_bbox(int(row['ymin']), int(row['xmax']), int(row['ymax']), int(row['xmin'])) for _, row in person_locations.iterrows()]
