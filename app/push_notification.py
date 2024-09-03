import requests

def send_pushover_notification(message, user_key, api_token):
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
