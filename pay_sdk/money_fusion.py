import requests
from .base import PaymentGateway, PaymentStatus, PaymentResponse
from typing import Optional, Dict, Any

class MoneyFusion(PaymentGateway):
    def __init__(self, api_url: str, status_url: str = "https://www.pay.moneyfusion.net/paiementNotif"):
        # Money Fusion docs say "apiUrl": "YOUR_API_URL" // Obtenez ceci depuis votre tableau de bord
        self.api_url = api_url
        self.status_url = status_url
        self.headers = {
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

        if not customer_phone:
            raise ValueError("customer_phone is required for Money Fusion")
        if not customer_name:
            # Money Fusion requires nomclient. We can default it if missing but better to enforce or use "Unknown".
            customer_name = "Customer"

        # Money Fusion requires 'article'. We'll create a dummy one.
        article = kwargs.get("article", [
            {
                "item": description or "Payment",
                "price": amount
            }
        ])

        payload = {
            "totalPrice": amount,
            "article": article,
            "personal_Info": kwargs.get("personal_Info", [{"orderId": order_id}]),
            "numeroSend": customer_phone,
            "nomclient": customer_name,
            "return_url": return_url,
            "webhook_url": webhook_url
        }

        # Remove None values if necessary, but Money Fusion might expect keys.
        # Docs say return_url and webhook_url are Not Required (Non).

        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if not data.get("statut"):
            raise Exception(f"Money Fusion Error: {data.get('message')}")

        return PaymentResponse(
            payment_url=data.get("url"),
            transaction_id=data.get("token"), # Money Fusion uses token for status check
            raw_response=data
        )

    def check_status(self, transaction_id: str) -> PaymentStatus:
        # transaction_id is the token
        url = f"{self.status_url}/{transaction_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # { "statut": true, "data": { "statut": "paid", ... } }

        if not data.get("statut"):
             # If top level status is false, maybe token not found?
             return PaymentStatus.UNKNOWN

        inner_data = data.get("data", {})
        status_str = inner_data.get("statut", "").lower()

        # Status mappings from docs:
        # pending -> Le paiement est en cours de traitement
        # failure -> Échec du paiement
        # no paid -> Paiement non effectué (maybe same as pending or canceled?)
        # paid -> Paiement réussi

        if status_str == "paid":
            return PaymentStatus.PAID
        elif status_str == "failure":
            return PaymentStatus.FAILED
        elif status_str == "pending":
            return PaymentStatus.PENDING
        elif status_str == "no paid":
            # "no paid" implies it hasn't been paid yet, possibly pending or user abandoned.
            return PaymentStatus.PENDING
        else:
            return PaymentStatus.UNKNOWN
