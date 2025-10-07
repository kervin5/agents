from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests


class PushNotification(BaseModel):
    """A message to be sent to the user"""
    message: str = Field(..., description="The message to be sent to the user.")

class PushNotificationTool(BaseTool):
    

    name: str = "Send a Push Notification"
    description: str = (
        "This tool is used to send a push notification to the user."
    )
    args_schema: Type[BaseModel] = PushNotification

    def _run(self, message: str) -> str:
        ntfy_topic = os.getenv("NTFY_TOPIC")
        ntfy_url = f"https://ntfy.sh/{ntfy_topic}"

        print(f"Push: {message}")
        if ntfy_topic:
            print("Sending push notification...")
            requests.post(ntfy_url, data=message.encode("utf-8"))
        else:
            print("No NTFY_TOPIC set, skipping push notification.")
        return '{"notification": "ok"}'