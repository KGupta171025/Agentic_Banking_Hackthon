"""
Airwallex Sandbox API Client.
Handles authentication, global accounts, balance queries, deposits, transfers, and card issuing.
Adheres strictly to the Airwallex Developer Guide:
- Token auto-refresh (valid 30 minutes)
- Reusable request_id for retries (idempotency)
- Major unit amounts (100 = $100.00)
"""

import time
import uuid
from typing import Any, Dict, List, Optional
import httpx


class AirwallexClient:
    def __init__(
        self,
        client_id: str,
        api_key: str,
        base_url: str = "https://api-sandbox.airwallex.com",
    ):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def _get_headers(self, requires_auth: bool = True) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if requires_auth:
            token = self.get_auth_token()
            headers["Authorization"] = f"Bearer {token}"
        else:
            headers["x-client-id"] = self.client_id
            headers["x-api-key"] = self.api_key
        return headers

    def get_auth_token(self) -> str:
        """Authenticate or return active cached token. Valid for 30 minutes."""
        now = time.time()
        # Refresh 2 minutes before expiration
        if self._token and now < (self._token_expires_at - 120):
            return self._token

        url = f"{self.base_url}/api/v1/authentication/login"
        headers = self._get_headers(requires_auth=False)
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            self._token = data.get("token")
            # Airwallex tokens expire in 30 minutes (1800 seconds)
            self._token_expires_at = now + 1800
            return self._token

    # ----------------------------------------------------
    # Global Accounts
    # ----------------------------------------------------
    def list_global_accounts(self) -> List[Dict[str, Any]]:
        """List all global accounts."""
        url = f"{self.base_url}/api/v1/global_accounts"
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json().get("items", [])

    def create_global_account(
        self,
        country_code: str = "US",
        currency: str = "USD",
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a global account with local rail feature."""
        url = f"{self.base_url}/api/v1/global_accounts/create"
        payload = {
            "request_id": request_id or str(uuid.uuid4()),
            "country_code": country_code,
            "required_features": [{"currency": currency, "transfer_method": "LOCAL"}],
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=self._get_headers(), json=payload)
            resp.raise_for_status()
            return resp.json()

    # ----------------------------------------------------
    # Balances
    # ----------------------------------------------------
    def get_current_balances(self) -> List[Dict[str, Any]]:
        """Retrieve multi-currency wallet balances."""
        url = f"{self.base_url}/api/v1/balances/current"
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json().get("items", [])

    # ----------------------------------------------------
    # Sandbox Simulation
    # ----------------------------------------------------
    def simulate_deposit(
        self,
        global_account_id: str,
        amount: float = 25000.0,
        currency: str = "USD",
        payer_name: str = "Seed funding",
    ) -> Dict[str, Any]:
        """Simulate incoming funds into a global account (major units)."""
        url = f"{self.base_url}/api/v1/simulation/deposit/create"
        payload = {
            "global_account_id": global_account_id,
            "amount": amount,
            "currency": currency,
            "payer_name": payer_name,
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=self._get_headers(), json=payload)
            resp.raise_for_status()
            return resp.json()

    # ----------------------------------------------------
    # Payouts & Transfers
    # ----------------------------------------------------
    def get_transfer_details(self, transfer_id: str) -> Dict[str, Any]:
        """Inspect status, UETR, and metadata of a transfer."""
        url = f"{self.base_url}/api/v1/transfers/{transfer_id}"
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()

    def cancel_transfer(self, transfer_id: str) -> Dict[str, Any]:
        """Atomic cancellation of an in-flight transfer."""
        url = f"{self.base_url}/api/v1/transfers/{transfer_id}/cancel"
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()

    def simulate_transfer_transition(
        self, transfer_id: str, target_status: str
    ) -> Dict[str, Any]:
        """Simulate status transition for testing (e.g. SENT, PAID, FAILED)."""
        url = f"{self.base_url}/api/v1/simulation/transfers/{transfer_id}/transition"
        payload = {"status": target_status}
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=self._get_headers(), json=payload)
            resp.raise_for_status()
            return resp.json()

    # ----------------------------------------------------
    # Issuing (Virtual Cards for Emergency Settlement)
    # ----------------------------------------------------
    def issue_emergency_virtual_card(
        self,
        cardholder_id: str,
        amount_limit: float,
        currency: str = "USD",
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Issue purpose-bound single-use virtual card with strict authorization limits."""
        url = f"{self.base_url}/api/v1/issuing/cards/create"
        payload = {
            "request_id": request_id or str(uuid.uuid4()),
            "cardholder_id": cardholder_id,
            "card_type": "VIRTUAL",
            "currency": currency,
            "authorization_controls": {
                "transaction_limits": [
                    {
                        "amount": amount_limit,
                        "currency": currency,
                        "interval": "PER_TRANSACTION",
                    }
                ]
            },
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=self._get_headers(), json=payload)
            resp.raise_for_status()
            return resp.json()
