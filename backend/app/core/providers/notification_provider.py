from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.observability import logger

class BaseNotificationProvider(ABC):
    @abstractmethod
    async def send(self, recipient: str, title: str, message: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        pass

class InAppNotificationProvider(BaseNotificationProvider):
    async def send(self, recipient: str, title: str, message: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        logger.info(f"InAppNotification delivered to {recipient}: [{title}] {message}")
        return True

class EmailNotificationProvider(BaseNotificationProvider):
    async def send(self, recipient: str, title: str, message: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        # Transactional email adapter: prints structured dispatch and logs event
        logger.info(f"EmailNotification dispatched to {recipient} | Subject: {title} | Body: {message}")
        return True

class CompositeNotificationService:
    def __init__(self):
        self.in_app = InAppNotificationProvider()
        self.email = EmailNotificationProvider()

    async def notify(
        self,
        recipient: str,
        title: str,
        message: str,
        notification_type: str = "GENERAL",
        send_email: bool = False,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        in_app_ok = await self.in_app.send(recipient, title, message, payload)
        email_ok = await self.email.send(recipient, title, message, payload) if send_email else False
        return {
            "recipient": recipient,
            "title": title,
            "notification_type": notification_type,
            "in_app_delivered": in_app_ok,
            "email_delivered": email_ok
        }

notification_service = CompositeNotificationService()

