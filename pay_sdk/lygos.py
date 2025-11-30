import requests
from .base import PaymentGateway, PaymentStatus, PaymentResponse
from typing import Optional, Dict, Any

class Lygos(PaymentGateway):
    BASE_URL = "https://api.lygosapp.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_payment(self,
                       amount: float,
                       order_id: str,
                       customer_name: Optional[str] = None,
                       customer_phone: Optional[str] = None,
                       return_url: Optional[str] = None,
                       cancel_url: Optional[str] = None,
                       webhook_url: Optional[str] = None,
                       description: Optional[str] = None,
                       **kwargs) -> PaymentResponse:

        # Lygos requires shop_name, but it's not in the generic interface.
        # We can accept it via kwargs or default it.
        shop_name = kwargs.get("shop_name", "My Shop")

        # Validate amount is integer-like
        if not float(amount).is_integer():
             raise ValueError(f"Lygos requires integer amounts. {amount} is not an integer.")

        amount_int = int(amount)

        payload = {
            "amount": amount_int,
            "shop_name": shop_name,
            "order_id": order_id,
            "message": description or "",
            "success_url": return_url or "",
            "failure_url": cancel_url or ""
        }

        url = f"{self.BASE_URL}/gateway"
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()

        return PaymentResponse(
            payment_url=data.get("link"),
            transaction_id=order_id, # Lygos status check uses order_id
            raw_response=data
        )

    def check_status(self, transaction_id: str) -> PaymentStatus:
        # transaction_id here is the order_id
        url = f"{self.BASE_URL}/gateway/payin/{transaction_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 404:
            return PaymentStatus.UNKNOWN

        response.raise_for_status()
        data = response.json()

        status_str = data.get("status", "").lower()

        # Map Lygos status to PaymentStatus
        if status_str in ["success", "successful", "paid", "completed"]:
            return PaymentStatus.PAID
        elif status_str in ["failed", "failure"]:
            return PaymentStatus.FAILED
        elif status_str in ["pending", "processing"]:
            return PaymentStatus.PENDING
        elif status_str in ["canceled", "cancelled"]:
            return PaymentStatus.CANCELED
        else:
            return PaymentStatus.UNKNOWN
