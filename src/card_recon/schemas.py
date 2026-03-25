from __future__ import annotations

FIELD_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "global_payments": {
        "card_brand": ("PAYMENT METHOD", "CARD BRAND", "CARD TYPE"),
        "batch_control": ("BATCH CONTROL NUMBER", "BATCH CONTROL", "BATCH"),
        "authorization_code": (
            "AUTHORIZATION CODE",
            "APPROVAL CODE",
            "AUTH CODE",
            "AUTHCODE",
        ),
        "amount": (
            "ORIGINAL TRANSACTION AMOUNT",
            "SETTLEMENT AMOUNT",
            "SETTLED AMOUNT",
            "AMOUNT",
        ),
        "transaction_date": (
            "PROCESSING DATE",
            "PROCESS DATE",
            "TRANSACTION DATE",
            "ORIGINAL TRANSACTION DATE",
        ),
        "card_number": ("CARD NUMBER", "PAN"),
    },
    "versapay": {
        "card_brand": (
            "CARD BRAND",
            "CARD TYPE",
            "PAYMENT METHOD",
            "CARDTYPE",
            "CC TYPE",
            "TYPE",
        ),
        "batch_control": ("BATCH ID", "BATCH", "BATCHCONTROL", "BATCH CONTROL"),
        "authorization_code": (
            "AUTH CODE",
            "AUTHORIZATION CODE",
            "AUTH CODE ",
            "AUTH_CODE",
            "AUTHCODE",
        ),
        "amount": ("AMOUNT", "TOTAL", "TRANSACTION AMOUNT"),
        "transaction_type": ("TYPE", "TRANSACTION TYPE"),
        "card_number": ("CARD NUMBER", "ACCOUNT", "CARD NO", "CC NUMBER", "PAN"),
    },
}


def normalize_header(header: str) -> str:
    return " ".join((header or "").strip().upper().replace("_", " ").split())
