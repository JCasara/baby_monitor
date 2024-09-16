from abc import ABC, abstractmethod

from app.states.state_classes import State


class StateManagerInterface(ABC):
    @abstractmethod
    def __init__(self):
        self.state = None
        self.no_face_count: int = 0
        self.max_no_face_count: int = 100
        self.pushover_service = None
        self.message: str = ''

    @abstractmethod
    def transition_state(self, person_detected, face_detected) -> None:
        """Transitions state machine to new state."""
        pass

    @abstractmethod
    def get_state(self) -> State:
        """Retreives current state."""
        pass

    @abstractmethod
    def set_state(self) -> None:
        """Sets current state."""
        pass
