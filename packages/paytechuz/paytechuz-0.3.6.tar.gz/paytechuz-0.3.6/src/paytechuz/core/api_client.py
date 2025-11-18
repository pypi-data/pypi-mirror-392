import os

from typing import Any, Dict, Optional

from .http import HttpClient
from .exceptions import AuthenticationError


class PaytechuzApiClient:
    """
    PayTechUZ API client
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.base_url = (
            base_url
            or os.getenv("PAYTECHUZ_API_BASE_URL")
            or "https://api.pay-tech.uz"
        )
        headers = {"Authorization": f"Bearer {self.api_key}"}
        self.http_client = HttpClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

    def create_payment(self, gateway: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payment
        """
        data: Dict[str, Any] = {"gateway": gateway}
        data.update(payload)
        return self.http_client.post("/v1/payments", json_data=data)

    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check payment status
        """
        endpoint = f"/v1/payments/{transaction_id}"
        return self.http_client.get(endpoint)

    def cancel_payment(
        self,
        transaction_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cancel a payment
        """
        endpoint = f"/v1/payments/{transaction_id}/cancel"
        data: Dict[str, Any] = {}
        if reason is not None:
            data["reason"] = reason
        return self.http_client.post(endpoint, json_data=data)
