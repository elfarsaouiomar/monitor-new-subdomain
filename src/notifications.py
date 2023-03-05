from requests import post
from termcolor import colored
from src.config import SLACK_WEBHOOK_URL, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from src.functions import custom_logger


class notifications:
    logger = custom_logger("notifications") 

    headers = {"Content-Type": "application/json"}

    def telegrame(self, message):
        """  Send message to Telegram """

        telegramUrl = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        params = {"text": f"🆕 {message}" , "chat_id": TELEGRAM_CHAT_ID, "parse_mode": "Markdown"}

        req = post(url=telegramUrl, 
                    params=params,
                    headers=self.headers
                )

        if req.status_code == 429:
            self.logger.error(f"Api Rate limit: {req.status_code} {req.json()}")

        if req.status_code != 200:
            self.logger.error(f"{req.status_code} {req.json()}")          

    def slack(self, message):
        """ send message to slack """

        data = {"text": f":new: {message}"}

        req = post(url=SLACK_WEBHOOK_URL, 
                    json=data,
                    headers=self.headers
                )
        
        if req.status_code == 429:
            self.logger.error(f"Api Rate limit: {req.status_code} {req.json()}")

        if req.status_code != 200:
            self.logger.error(f"{req.status_code} {req.json()}")

