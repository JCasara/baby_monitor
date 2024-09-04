from enum import Enum, auto

import requests


class DetectionState(Enum):
    IDLE = auto()
    PERSON_DETECTED = auto()
    FACE_DETECTED = auto()
    NO_FACE_DETECTED = auto()


class StateManager:
    def __init__(self, threshold_config, pushover_config):
        self.state = DetectionState.IDLE
        self.no_face_count = 0
        self.threshold_config = threshold_config
        self.max_no_face_count = threshold_config.get('detection_threshold')
        self.pushover_config = pushover_config

    def send_pushover_notification(self):
        if self.pushover_config:
            api_token = self.pushover_config.get('API_TOKEN')
            user_key = self.pushover_config.get('USER_KEY')
            message = self.pushover_config.get('MESSAGE')

        url = "https://api.pushover.net/1/messages.json"
        data = {
            "token": api_token,
            "user": user_key,
            "message": message
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print(f"Failed to send notification: {response.status_code}")
            print(response.text)

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
                        # self._send_pushover_notification()
                else:
                    if self.state != DetectionState.PERSON_DETECTED:
                        self.state = DetectionState.PERSON_DETECTED
        else:
            if self.state != DetectionState.IDLE:
                self.state = DetectionState.IDLE
                self.no_face_count = 0  # Reset the counter if no person is detected

    def get_state(self):
        return self.state
