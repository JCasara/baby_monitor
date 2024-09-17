from app.interfaces.state_manager_interface import StateManagerInterface
from app.services.pushover_service import PushoverService
from app.states.state_classes import IdleState, State


class StateManagerService(StateManagerInterface):
    def __init__(self, config: dict, pushover_service: PushoverService):
        self.state = IdleState(self)
        self.no_face_count = 0
        self.max_no_face_count = config['threshold'].get('detection_threshold')
        self.pushover_service = pushover_service
        self.message = config['pushover'].get('MESSAGE', 'No message provided!')

    def set_state(self, state: State) -> None:
        """Set a new state."""
        self.state = state

    def process_frame(self, person_detected: bool, face_detected: bool) -> None:
        """Delegate frame processing to the current state."""
        self.state.process_frame(person_detected, face_detected)

    def get_state(self) -> State:
        """Get the current state."""
        return self.state
