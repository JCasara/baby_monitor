from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self, state_manager):
        self.state_manager = state_manager

    @abstractmethod
    def process_frame(self, person_detected: bool, face_detected: bool):
        pass

    @abstractmethod
    def get_annotation(self) -> str:
        pass

    @abstractmethod
    def get_color(self) -> tuple:
        pass

class IdleState(State):
    def process_frame(self, person_detected: bool, face_detected: bool):
        if person_detected:
            self.state_manager.set_state(PersonDetectedState(self.state_manager))
    
    def get_annotation(self) -> str:
        return "Idle"
    
    def get_color(self) -> tuple:
        return (255, 255, 255)

class PersonDetectedState(State):
    def process_frame(self, person_detected: bool, face_detected: bool):
        if face_detected:
            self.state_manager.set_state(FaceDetectedState(self.state_manager))
        else:
            self.state_manager.no_face_count += 1
            if self.state_manager.no_face_count >= self.state_manager.max_no_face_count:
                self.state_manager.set_state(NoFaceDetectedState(self.state_manager))
                self.state_manager.pushover_service.send_notification(self.state_manager.message)
            elif not person_detected:
                self.state_manager.set_state(IdleState(self.state_manager))
    
    def get_annotation(self) -> str:
        return "Person"
    
    def get_color(self) -> tuple:
        return (255, 0, 0)

class FaceDetectedState(State):
    def process_frame(self, person_detected: bool, face_detected: bool):
        if not face_detected:
            self.state_manager.set_state(PersonDetectedState(self.state_manager))
    
    def get_annotation(self) -> str:
        return "Face"
    
    def get_color(self) -> tuple:
        return (0, 255, 0)

class NoFaceDetectedState(State):
    def process_frame(self, person_detected: bool, face_detected: bool):
        if person_detected:
            self.state_manager.no_face_count = 0
            if face_detected:
                self.state_manager.set_state(FaceDetectedState(self.state_manager))
            else:
                self.state_manager.set_state(PersonDetectedState(self.state_manager))
    
    def get_annotation(self) -> str:
        return "Face Not Detected"
    
    def get_color(self) -> tuple:
        return (0, 0, 255)
