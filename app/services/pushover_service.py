import requests

from app.interfaces.notification_interface import NotificationInterface


class PushoverService(NotificationInterface):
    def __init__(self, api_token: str, user_key: str):
        self.api_token: str = api_token
        self.user_key: str = user_key

    def send_notification(self, message: str) -> None:
        print(message)
        url: str = "https://api.pushover.net/1/messages.json"
        data: dict = {
            "token": self.api_token,
            "user": self.user_key,
            "message": message
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print(f"Failed to send notification: {response.status_code}")
            print(response.text)
