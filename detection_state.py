from enum import Enum, auto

class DetectionState(Enum):
    FACE_DETECTED = auto()
    FACE_NOT_DETECTED = auto()

class StateManager:
    def __init__(self, max_no_face_count=100):
        self.state = DetectionState.FACE_DETECTED
        self.no_face_count = 0
        self.max_no_face_count = max_no_face_count

    def transition_state(self, face_detected):
        """Handle state transitions based on face detection."""
        if face_detected:
            self.no_face_count = 0
            if self.state != DetectionState.FACE_DETECTED:
                self.state = DetectionState.FACE_DETECTED
        else:
            self.no_face_count += 1
            if self.no_face_count >= self.max_no_face_count:
                if self.state != DetectionState.FACE_NOT_DETECTED:
                    self.state = DetectionState.FACE_NOT_DETECTED

    def get_state(self):
        return self.state

