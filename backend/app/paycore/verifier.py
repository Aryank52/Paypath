from typing import Dict, Any, Tuple
from app.paycore.client import paypal_client
from app.core.observability import logger

class IndependentPaymentVerifier:
    """
    Independent Verification Engine:
    Re-reads authoritative PayPal resources directly and performs exact comparison
    against expected amounts, currencies, and completion states.
    """

    @staticmethod
    async def verify_capture(
        capture_id: str,
        expected_amount: float,
        expected_currency: str = "USD"
    ) -> Tuple[bool, Dict[str, Any]]:
        try:
            details = await paypal_client.get_capture_details(capture_id)
            status = details.get("status")
            amount_obj = details.get("amount", {})
            actual_amount = float(amount_obj.get("value", 0.0))
            actual_currency = amount_obj.get("currency_code", "USD")

            # Check status and amounts
            status_ok = status in ["COMPLETED", "PARTIALLY_REFUNDED"]
            amount_ok = abs(actual_amount - expected_amount) < 0.01
            currency_ok = actual_currency.upper() == expected_currency.upper()

            is_verified = status_ok and amount_ok and currency_ok
            logger.info(
                f"Independent verification for capture {capture_id}: "
                f"status_ok={status_ok}, amount_ok={amount_ok}, currency_ok={currency_ok} -> {is_verified}"
            )
            return is_verified, details
        except Exception as e:
            logger.error(f"Error during independent capture verification: {e}")
            return False, {"error": str(e)}

    @staticmethod
    async def verify_refund(
        refund_id: str,
        expected_amount: float,
        expected_currency: str = "USD"
    ) -> Tuple[bool, Dict[str, Any]]:
        try:
            details = await paypal_client.get_refund_details(refund_id)
            status = details.get("status")
            amount_obj = details.get("amount", {})
            actual_amount = float(amount_obj.get("value", 0.0))
            actual_currency = amount_obj.get("currency_code", "USD")

            status_ok = status == "COMPLETED"
            amount_ok = abs(actual_amount - expected_amount) < 0.01
            currency_ok = actual_currency.upper() == expected_currency.upper()

            is_verified = status_ok and amount_ok and currency_ok
            logger.info(
                f"Independent verification for refund {refund_id}: "
                f"status_ok={status_ok}, amount_ok={amount_ok}, currency_ok={currency_ok} -> {is_verified}"
            )
            return is_verified, details
        except Exception as e:
            logger.error(f"Error during independent refund verification: {e}")
            return False, {"error": str(e)}

payment_verifier = IndependentPaymentVerifier()

