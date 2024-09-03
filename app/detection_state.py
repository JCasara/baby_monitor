from enum import Enum, auto

from app.push_notification import send_pushover_notification


class DetectionState(Enum):
    IDLE = auto()
    PERSON_DETECTED = auto()
    FACE_DETECTED = auto()
    NO_FACE_DETECTED = auto()


class StateManager:
    def __init__(self, max_no_face_count=100, pushover_config=None):
        self.state = DetectionState.IDLE
        self.no_face_count = 0
        self.max_no_face_count = max_no_face_count
        self.pushover_config = pushover_config

    def _send_pushover_notification(self):
        if self.pushover_config:
            message = self.pushover_config.get('MESSAGE')
            user_key = self.pushover_config.get('USER_KEY')
            api_token = self.pushover_config.get('API_TOKEN')
            send_pushover_notification(message, user_key, api_token)

    def process_frame(self, person_detected, face_detected):
        """Handle state transitions based on detection results."""
        if self.state == DetectionState.IDLE:
            if person_detected:
                self.transition_state(person_detected, True)
        elif self.state in [DetectionState.PERSON_DETECTED, DetectionState.FACE_DETECTED]:
            self.transition_state(person_detected, face_detected)

    def transition_state(self, person_detected, face_detected):
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
                        self._send_pushover_notification()
                else:
                    if self.state != DetectionState.PERSON_DETECTED:
                        self.state = DetectionState.PERSON_DETECTED
        else:
            if self.state != DetectionState.IDLE:
                self.state = DetectionState.IDLE
                self.no_face_count = 0  # Reset the counter if no person is detected

    def get_state(self):
        return self.state
