from enum import Enum, auto

from app.services.pushover_service import PushoverService


class DetectionState(Enum):
    IDLE = auto()
    PERSON_DETECTED = auto()
    FACE_DETECTED = auto()
    NO_FACE_DETECTED = auto()

class StateManager:
    def __init__(self, config, pushover_service: PushoverService):
        self.state = DetectionState.IDLE
        self.no_face_count = 0
        self.max_no_face_count = config['threshold'].get('detection_threshold')
        self.pushover_service = pushover_service
        self.message = config['pushover'].get('MESSAGE', 'No message provided!')

    def process_frame(self, person_detected: bool, face_detected: bool) -> None:
        """Handle state transitions based on detection results."""
        if person_detected:
            if face_detected:
                self.transition_state(True, True)
            else:
                self.transition_state(True, False)
        else:
            self.transition_state(False, False)
        
    def transition_state(self, person_detected: bool, face_detected: bool) -> None:
        """Handle state transitions based on detection results."""
        if person_detected:
            if face_detected:
                if self.state != DetectionState.FACE_DETECTED:
                    self.state = DetectionState.FACE_DETECTED
                    self.no_face_count = 0
            else:
                self.no_face_count += 1
                if self.no_face_count >= self.max_no_face_count:
                    if self.state != DetectionState.NO_FACE_DETECTED:
                        self.state = DetectionState.NO_FACE_DETECTED
                        self.pushover_service.send_notification(self.message)
                else:
                    if self.state != DetectionState.PERSON_DETECTED:
                        self.state = DetectionState.PERSON_DETECTED
        else:
            if self.state != DetectionState.IDLE:
                self.state = DetectionState.IDLE
                self.no_face_count = 0  # Reset the counter if no person is detected

    def get_state(self) -> DetectionState:
        return self.state
