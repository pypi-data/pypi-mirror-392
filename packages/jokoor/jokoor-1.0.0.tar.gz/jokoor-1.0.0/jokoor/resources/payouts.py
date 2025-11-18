"""
Payouts resource for the Jokoor SDK
"""

from typing import Optional, Dict, Any, Tuple

from ..types import PayoutBalance, PayoutRequest, PaginatedResponse
from ..http_client import HTTPClient


class PayoutsResource:
    """Payout operations"""

    def __init__(self, http_client: HTTPClient) -> None:
        self._http = http_client

    def get_balance(self) -> Tuple[Optional[PayoutBalance], Optional[str]]:
        """Get payout balance"""
        response, error = self._http.get("/v1/payouts/balance")
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def create_request(
        self, *, amount: str, bank_account_id: str, otp_code: str
    ) -> Tuple[Optional[PayoutRequest], Optional[str]]:
        """Create a payout request (requires OTP)"""
        data = {"amount": amount, "bank_account_id": bank_account_id, "otp_code": otp_code}
        response, error = self._http.post("/v1/payouts/requests", data)
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def get_request(self, request_id: str) -> Tuple[Optional[PayoutRequest], Optional[str]]:
        """Get payout request details"""
        response, error = self._http.get(f"/v1/payouts/requests/{request_id}")
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def list_requests(
        self, *, offset: int = 0, limit: int = 20, status: Optional[str] = None
    ) -> Tuple[Optional[PaginatedResponse], Optional[str]]:
        """List payout requests"""
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status

        response, error = self._http.get("/v1/payouts/requests", params)
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore

    def cancel_request(
        self, request_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Cancel a pending payout request"""
        response, error = self._http.put(f"/v1/payouts/requests/{request_id}/cancel")
        if error:
            return (None, str(error))
        return (response, None)  # type: ignore
