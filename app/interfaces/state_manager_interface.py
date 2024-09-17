from abc import ABC, abstractmethod

from app.states.state_classes import IdleState, State


class StateManagerInterface(ABC):
    @abstractmethod
    def __init__(self, config, pushover_service):
        self.state: State = IdleState(self)
        self.no_face_count: int = 0
        self.max_no_face_count: int = 100
        self.pushover_service = None
        self.message: str = ''

    @abstractmethod
    def process_frame(self, person_detected: bool, face_detected: bool) -> None:
        """Delegate frame processing to the current state."""
        self.state.process_frame(person_detected, face_detected)

    @abstractmethod
    def get_state(self) -> State:
        """Retreives current state."""
        pass

    @abstractmethod
    def set_state(self, state: State) -> None:
        """Sets current state."""
        pass
