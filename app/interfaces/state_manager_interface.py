from abc import ABC, abstractmethod


class StateManagerInterface(ABC):
    @abstractmethod
    def transition_state(self, person_detected, face_detected):
        pass

    @abstractmethod
    def get_state(self):
        pass
