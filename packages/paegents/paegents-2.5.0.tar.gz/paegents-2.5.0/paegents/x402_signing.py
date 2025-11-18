"""
Client-side x402 payment signing for secure stablecoin payments.

Agents use this to create signed payment authorizations WITHOUT sending
their private keys to the server. This is the production-ready approach.
"""
from __future__ import annotations

from typing import Any, Dict

from eth_account import Account
from x402.clients.base import x402Client
from x402.chains import get_chain_id, get_default_token_address, get_token_decimals
from x402.types import PaymentRequirements
from decimal import Decimal, ROUND_HALF_UP


def create_signed_x402_payment(
    *,
    payer_private_key: str,
    destination_wallet: str,
    amount_cents: int,
    currency: str = "usd",
    network: str = "base-sepolia",
    resource_id: str,
    description: str = "Agent payment",
    max_timeout_seconds: int = 600,
) -> str:
    """
    Create a signed x402 payment header that can be sent to the API.

    This function is called BY THE AGENT (client-side) to sign a payment
    with their private key. The private key NEVER leaves the agent's environment.

    Args:
        payer_private_key: Agent's private key (stays local, never sent to server)
        destination_wallet: Where to send funds (seller's wallet)
        amount_cents: Amount in cents
        currency: Currency code (default: usd)
        network: Blockchain network (default: base-sepolia for testnet)
        resource_id: Unique identifier for this payment (e.g., "agreement:agree_123")
        description: Human-readable description
        max_timeout_seconds: Payment validity window

    Returns:
        Base64-encoded signed payment header (safe to send to server)

    Example:
        >>> # Agent creates signed payment locally
        >>> payment_header = create_signed_x402_payment(
        ...     payer_private_key=my_private_key,  # Stays local!
        ...     destination_wallet="0xSeller...",
        ...     amount_cents=500,  # $5.00
        ...     resource_id="agreement:agree_abc123"
        ... )
        >>> # Send only the signature to API
        >>> payment_method = {
        ...     "rail": "stablecoin",
        ...     "provider": "coinbase",
        ...     "wallet_address": "0xSeller...",
        ...     "payment_header": payment_header  # Secure!
        ... }
    """
    # Ensure private key has 0x prefix
    if not payer_private_key.startswith("0x"):
        payer_private_key = f"0x{payer_private_key}"

    # Get blockchain parameters
    chain_id = get_chain_id(network)
    asset_address = get_default_token_address(chain_id)  # USDC on base-sepolia
    token_decimals = get_token_decimals(chain_id, asset_address)

    # Convert cents to atomic units (e.g., USDC has 6 decimals)
    amount_dollars = Decimal(amount_cents) / Decimal(100)
    atomic_amount = amount_dollars * (Decimal(10) ** Decimal(token_decimals))
    atomic_amount_int = int(atomic_amount.quantize(Decimal(1), rounding=ROUND_HALF_UP))

    # Create payment requirements
    payment_requirements = PaymentRequirements(
        scheme="exact",
        network=network,
        maxAmountRequired=str(atomic_amount_int),
        resource=resource_id,
        description=description,
        mimeType="application/json",
        payTo=destination_wallet,
        maxTimeoutSeconds=max_timeout_seconds,
        asset=asset_address,
        extra={"name": "USD Coin", "version": "2"},
    )

    # Create account from private key (THIS STAYS LOCAL)
    account = Account.from_key(payer_private_key)

    # Create x402 client and sign
    client = x402Client(account)
    payment_header = client.create_payment_header(payment_requirements)

    # Return only the signed header (NOT the private key!)
    return payment_header
