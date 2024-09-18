"""Constants used in project"""
from typing import Tuple

import cv2

# Font Settings
FONT_FACE: int = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE: int = 1
LINE_THICKNESS: int = 2
ORG: Tuple[int, int] = (10, 30)


# Colors
RED: Tuple[int, int, int] = (255, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
BLUE: Tuple[int, int, int] = (0, 0, 255)
WHITE: Tuple[int, int, int] = (255, 255, 255)
