import logging
from requests import post

from src.core.config import settings

logger = logging.getLogger(__name__)


class Notifications:
    headers = {"Content-Type": "application/json"}

    def telegram(self, message):
        """Send message to Telegram"""

        telegramUrl = (
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        params = {
            "text": f"🆕 {message}",
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "parse_mode": "Markdown",
        }

        req = post(url=telegramUrl, params=params, headers=self.headers)

        if req.status_code == 429:
            logger.error(f"Api Rate limit: {req.status_code} {req.json()}")

        if req.status_code != 200:
            logger.error(f"{req.status_code} {req.json()}")

    def slack(self, message):
        """send message to slack"""

        data = {"text": f":new: {message}"}

        req = post(url=settings.SLACK_WEBHOOK, json=data, headers=self.headers)

        if req.status_code == 429:
            logger.error(f"Api Rate limit: {req.status_code} {req.json()}")

        if req.status_code != 200:
            logger.error(f"{req.status_code} {req.json()}")
