import asyncio
from typing import List, Tuple

import cv2
import face_recognition
import numpy as np
import torch
from torch.nn import Module

from app.interfaces.detection_interface import DetectionInterface


class DetectionService(DetectionInterface):
    def __init__(self, scale_factor: int):
        self.yolo_model: Module = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.scale_factor: int = scale_factor

    def _scale_bbox(self, top: int, right: int, bottom: int, left: int) -> Tuple[int, int, int, int]:
        """Scales bounding boxes based on scale_factor."""
        return (int(top / self.scale_factor), int(right / self.scale_factor),
                int(bottom / self.scale_factor), int(left / self.scale_factor))
    
    async def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for faces detected in the frame."""
        return await asyncio.to_thread(self._detect_faces_sync, frame)

    def _detect_faces_sync(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for faces detected in the frame."""
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        return [self._scale_bbox(top, right, bottom, left) for (top, right, bottom, left) in face_locations]

    async def detect_objects(self, frame: np.ndarray, object_class: str) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for detected objects of a specified class in the frame."""
        return await asyncio.to_thread(self._detect_objects_sync, frame, object_class)

    def _detect_objects_sync(self, frame: np.ndarray, object_class: str) -> List[Tuple[int, int, int, int]]:
        """Synchronous detection logic for objects."""
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        yolo_results = self.yolo_model(small_frame)
        yolo_locations = yolo_results.pandas().xyxy[0]
        person_locations = yolo_locations[yolo_locations['name'] == object_class]
        return [self._scale_bbox(int(row['ymin']), int(row['xmax']), int(row['ymax']), int(row['xmin'])) for _, row in person_locations.iterrows()]

    async def detect_persons(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Convenience function for detecting persons."""
        return await self.detect_objects(frame, 'person')

    async def detect_dogs(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Convenience function for detecting dogs."""
        return await self.detect_objects(frame, 'dog')
