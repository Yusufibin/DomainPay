from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"
    UNKNOWN = "unknown"

@dataclass
class PaymentResponse:
    payment_url: str
    transaction_id: str
    raw_response: Dict[str, Any]

class PaymentGateway(ABC):
    """
    Abstract base class for payment gateways.
    """

    @abstractmethod
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
        """
        Initiates a payment request.
        """
        pass

    @abstractmethod
    def check_status(self, transaction_id: str) -> PaymentStatus:
        """
        Checks the status of a payment.
        """
        pass
