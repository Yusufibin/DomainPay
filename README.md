# Payment SDK for Lygos and Money Fusion

A Python SDK to handle payments via Lygos and Money Fusion with a unified interface.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Initialization

```python
from pay_sdk import Lygos, MoneyFusion, PaymentStatus

# Initialize Lygos
lygos_client = Lygos(api_key="YOUR_LYGOS_API_KEY")

# Initialize Money Fusion
money_fusion_client = MoneyFusion(api_url="YOUR_MONEY_FUSION_API_URL")
```

### Creating a Payment

Both clients share the same `create_payment` interface.

```python
# Select your provider
client = lygos_client
# OR
# client = money_fusion_client

response = client.create_payment(
    amount=5000,
    order_id="ORD-12345",
    customer_phone="600000000", # Required for Money Fusion
    customer_name="John Doe",   # Required for Money Fusion
    description="Payment for Order #12345",
    return_url="https://myshop.com/callback",
    webhook_url="https://myshop.com/webhook"
)

print(f"Payment URL: {response.payment_url}")
print(f"Transaction ID: {response.transaction_id}")

# Redirect user to response.payment_url
```

### Checking Payment Status

```python
status = client.check_status(response.transaction_id)

if status == PaymentStatus.PAID:
    print("Payment successful!")
elif status == PaymentStatus.PENDING:
    print("Payment pending...")
elif status == PaymentStatus.FAILED:
    print("Payment failed.")
```

## Specifics

- **Lygos**:
  - Requires `api_key`.
  - `shop_name` can be passed in `kwargs` or defaults to "My Shop".
  - Uses `order_id` as the transaction identifier for status checks.

- **Money Fusion**:
  - Requires `api_url` (provided in your dashboard).
  - Requires `customer_phone`.
  - Uses a returned `token` as the transaction identifier for status checks.
