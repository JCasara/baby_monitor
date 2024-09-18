""" Utility script for opencv functions """
from typing import List, Tuple

import cv2
import numpy as np

from app.interfaces.state_manager_interface import State
from app.utils.constants import (FONT_FACE, FONT_SCALE, GREEN, LINE_THICKNESS,
                                 RED)


def display_fps(frame: np.ndarray, fps: float) -> None:
        """Display frame rate using cv2."""
        ORG: Tuple[int, int] = (10, 30)
        fps_text: str = f"FPS: {fps:.2f}"
        cv2.putText(frame, fps_text, ORG, FONT_FACE, FONT_SCALE, RED, LINE_THICKNESS)

def draw_bboxes(bbox_locations: List[Tuple[int, int, int, int]], frame: np.ndarray) -> None:
        """Draw bounding boxes for detections."""
        # Is there another way to draw the bboxes? Or can the bbox_locations be passed back to
        # the camera_service?
        for (top, right, bottom, left) in bbox_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), GREEN, LINE_THICKNESS)

def draw_annotations(frame: np.ndarray, state: State) -> None:
    """Draw annotations on image that indicate state."""
    # Is there another way to draw the annotations? Or can the annotations be passed back to
    # the camera_service?
    ORG: Tuple[int, int] = (10, 50) # Bottom-left corner of the text string in the image

    annotation_text: str = state.get_annotation()
    color: Tuple[int, int, int] = state.get_color()

    cv2.putText(frame, annotation_text, ORG, FONT_FACE, FONT_SCALE, color, LINE_THICKNESS)

def encode_image(frame: np.ndarray, encoding: str = '.jpg'):
    ret, encoded_data = cv2.imencode(encoding, frame)
    return ret, encoded_data

def resize_image(frame: np.ndarray, scale_factor: float):
    return cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)

def convert_bgr2rgb(frame: np.ndarray):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
