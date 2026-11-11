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

    async def send_verification_email(self, recipient: str, full_name: Optional[str], token: str) -> bool:
        """Dispatches email verification message with secure short-lived token."""
        title = "Verify Your PayPath Account"
        message = (
            f"Hello {full_name or 'there'},\n\n"
            f"Please verify your email address to complete your PayPath registration.\n"
            f"Your verification token is: {token}\n"
            f"This link expires in 24 hours.\n\n"
            f"If you did not create a PayPath account, please disregard this email."
        )
        return await self.email.send(recipient, title, message, {"event": "EMAIL_VERIFICATION"})

    async def send_password_reset_email(self, recipient: str, token: str) -> bool:
        """Dispatches password reset instructions with single-use token."""
        title = "PayPath Password Reset Request"
        message = (
            f"We received a request to reset your PayPath account password.\n"
            f"Use the following secure token to update your password:\n{token}\n"
            f"This token expires in 15 minutes and can only be used once.\n\n"
            f"If you did not request this, your account is secure and no action is needed."
        )
        return await self.email.send(recipient, title, message, {"event": "PASSWORD_RESET"})

    async def send_payment_confirmation(
        self,
        recipient: str,
        transaction_id: str,
        amount: float,
        currency: str,
        merchant_name: str
    ) -> bool:
        """Dispatches payment confirmation without raw financial credentials."""
        title = f"Payment Confirmed: ${amount:.2f} {currency} to {merchant_name}"
        message = (
            f"Your payment to {merchant_name} has been processed and verified.\n"
            f"Transaction ID: {transaction_id}\n"
            f"Amount: ${amount:.2f} {currency}\n"
            f"Status: COMPLETED\n"
            f"You can review this transaction and its AI intelligence profile anytime on your PayPath Dashboard."
        )
        return await self.email.send(recipient, title, message, {"event": "PAYMENT_CONFIRMATION", "tx_id": transaction_id})

    async def send_refund_confirmation(
        self,
        recipient: str,
        transaction_id: str,
        refund_amount: float,
        currency: str
    ) -> bool:
        """Dispatches verified refund notification."""
        title = f"Refund Processed: ${refund_amount:.2f} {currency}"
        message = (
            f"Your refund of ${refund_amount:.2f} {currency} for transaction {transaction_id} "
            f"has been verified through PayPal and credited to your original payment method."
        )
        return await self.email.send(recipient, title, message, {"event": "REFUND_CONFIRMATION", "tx_id": transaction_id})

    async def send_approval_required(
        self,
        recipient: str,
        transaction_id: str,
        amount: float,
        merchant_name: str
    ) -> bool:
        """Dispatches human-in-the-loop approval request."""
        title = f"Action Required: Approve Payment of ${amount:.2f} to {merchant_name}"
        message = (
            f"A pending payment requires your explicit review and authorization under Payment Guard policies.\n"
            f"Merchant: {merchant_name}\n"
            f"Amount: ${amount:.2f}\n"
            f"Transaction: {transaction_id}\n"
            f"Log in to your PayPath portal to review the policy details and approve or decline."
        )
        return await self.email.send(recipient, title, message, {"event": "APPROVAL_REQUIRED", "tx_id": transaction_id})

    async def send_security_alert(
        self,
        recipient: str,
        event_description: str
    ) -> bool:
        """Dispatches security alert notification."""
        title = "PayPath Security Alert"
        message = (
            f"A security event was logged for your PayPath account:\n\n"
            f"{event_description}\n\n"
            f"If this was not you, please log into PayPath and change your password immediately."
        )
        return await self.email.send(recipient, title, message, {"event": "SECURITY_ALERT"})

notification_service = CompositeNotificationService()

