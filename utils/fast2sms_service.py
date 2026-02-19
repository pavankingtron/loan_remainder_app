import os
import requests


class Fast2SMSService:

    def __init__(self):
        self.api_key = os.getenv("FAST2SMS_API_KEY")
        self.url = "https://www.fast2sms.com/dev/bulkV2"

    def send_sms(self, phone, message):

        payload = {
            "route": "q",
            "message": message,
            "language": "english",
            "numbers": phone
        }

        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=headers
            )

            result = response.json()

            if result.get("return") is True:
                return True
            else:
                print("Fast2SMS Error:", result)
                return False

        except Exception as e:
            print("SMS Exception:", e)
            return False
