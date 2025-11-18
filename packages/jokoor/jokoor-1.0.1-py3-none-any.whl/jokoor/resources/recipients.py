"""
Payout Recipients resource for the Jokoor SDK
"""

from typing import Optional, Dict, Any, List, Tuple

from ..types import PayoutRecipient, RecipientPayout, PaginatedResponse
from ..http_client import HTTPClient


class RecipientsResource:
    """Payout recipient operations (Wave B2P)"""

    def __init__(self, http_client: HTTPClient) -> None:
        self._http = http_client

    def create(
        self,
        *,
        name: str,
        phone: str,
        default_amount: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[PayoutRecipient], Optional[str]]:
        """Create a payout recipient"""
        data: Dict[str, Any] = {"name": name, "phone": phone}
        if default_amount:
            data["default_amount"] = default_amount
        if metadata:
            data["metadata"] = metadata

        response, error = self._http.post("/v1/payouts/recipients", data)
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def get(self, recipient_id: str) -> Tuple[Optional[PayoutRecipient], Optional[str]]:
        """Get recipient details"""
        response, error = self._http.get(f"/v1/payouts/recipients/{recipient_id}")
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def list(
        self, *, offset: int = 0, limit: int = 20
    ) -> Tuple[Optional[PaginatedResponse], Optional[str]]:
        """List payout recipients"""
        params = {"offset": offset, "limit": limit}
        response, error = self._http.get("/v1/payouts/recipients", params)
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def update(
        self,
        recipient_id: str,
        *,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        default_amount: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[PayoutRecipient], Optional[str]]:
        """Update recipient information"""
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if phone is not None:
            data["phone"] = phone
        if default_amount is not None:
            data["default_amount"] = default_amount
        if metadata is not None:
            data["metadata"] = metadata

        response, error = self._http.put(f"/v1/payouts/recipients/{recipient_id}", data)
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def delete(self, recipient_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Delete a payout recipient"""
        response, error = self._http.delete(f"/v1/payouts/recipients/{recipient_id}")
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def send_payout(
        self, *, recipient_id: str, amount: str, otp_code: str
    ) -> Tuple[Optional[RecipientPayout], Optional[str]]:
        """Send payout to recipient (requires OTP)"""
        data = {"recipient_id": recipient_id, "amount": amount, "otp_code": otp_code}
        response, error = self._http.post("/v1/payouts/recipients/send", data)
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def list_payouts(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        recipient_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[Optional[PaginatedResponse], Optional[str]]:
        """List recipient payouts"""
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if recipient_id:
            params["recipient_id"] = recipient_id
        if status:
            params["status"] = status

        response, error = self._http.get("/v1/payouts/recipients/payouts", params)
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def get_payout(self, payout_id: str) -> Tuple[Optional[RecipientPayout], Optional[str]]:
        """Get recipient payout details"""
        response, error = self._http.get(f"/v1/payouts/recipients/payouts/{payout_id}")
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def reverse_payout(
        self, payout_id: str, *, otp_code: str, reason: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Reverse a recipient payout (requires OTP)"""
        data: Dict[str, Any] = {"otp_code": otp_code}
        if reason:
            data["reason"] = reason

        response, error = self._http.post(
            f"/v1/payouts/recipients/payouts/{payout_id}/reverse", data
        )
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore
