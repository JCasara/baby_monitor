from abc import ABC, abstractmethod


class NotificationInterface(ABC):
    @abstractmethod
    def send_notification(self, message: str) -> None:
        """Send push notification to cell-phone."""
        pass
