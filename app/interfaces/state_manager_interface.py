from abc import ABC, abstractmethod
from typing import Optional

from app.interfaces.notification_interface import NotificationInterface
from app.states.state_classes import IdleState, State


class StateManagerInterface(ABC):
    @abstractmethod
    def __init__(self, config: dict, pushover_service: NotificationInterface):
        self.state: State = IdleState(self)
        self.no_face_count: int = 0
        self.max_no_face_count: int = 0
        self.pushover_service: NotificationInterface = pushover_service
        self.message: str = ""

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
