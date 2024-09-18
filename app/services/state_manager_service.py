from app.interfaces.notification_interface import NotificationInterface
from app.interfaces.state_manager_interface import StateManagerInterface
from app.states.state_classes import IdleState, State


class StateManagerService(StateManagerInterface):
    def __init__(self, config: dict, pushover_service: NotificationInterface):
        self.state: State = IdleState(self)
        self.no_face_count: int = 0
        self.max_no_face_count: int = config['threshold'].get('detection_threshold', 100)
        self.pushover_service: NotificationInterface = pushover_service
        self.message: str = config['pushover'].get('MESSAGE', 'No message provided!')

    def set_state(self, state: State) -> None:
        """Set a new state."""
        self.state = state

    def process_frame(self, person_detected: bool, face_detected: bool) -> None:
        """Delegate frame processing to the current state."""
        self.state.process_frame(person_detected, face_detected)

    def get_state(self) -> State:
        """Get the current state."""
        return self.state
