from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from .models import NormalizedRecord
from .schemas import FIELD_ALIASES, normalize_header


def resolve_field(row: dict[str, object], source_system: str, logical_field: str) -> str:
    aliases = FIELD_ALIASES[source_system][logical_field]
    normalized = {normalize_header(str(k)): v for k, v in row.items()}
    for alias in aliases:
        value = normalized.get(normalize_header(alias))
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return ""


def normalize_brand(raw_brand: str) -> str:
    token = normalize_header(raw_brand)
    if token in {"VI", "VISA"}:
        return "Visa"
    if token in {"MC", "MASTERCARD", "MASTERCARD"}:
        return "MC"
    if token in {"AE", "AX", "AMEX", "AMERICAN EXPRESS"}:
        return "Amex"
    return raw_brand.strip()


def normalize_amount(value: str) -> Decimal:
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return Decimal("0")
    return Decimal(cleaned)


def extract_card_last4(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    return digits[-4:] if len(digits) >= 4 else digits


def should_include_global_payments_row(row: dict[str, object]) -> bool:
    payment_method = normalize_header(str(row.get("Payment Method", "")))
    card_type = normalize_header(str(row.get("Card Type", "")))
    charge_type = normalize_header(str(row.get("Charge Type", "")))

    if payment_method == "ADJ":
        return False
    if "ADJUSTMENT" in card_type:
        return False
    if charge_type == "1901":
        return False
    return True


def normalize_global_payments(rows: Iterable[dict[str, object]]) -> list[NormalizedRecord]:
    normalized: list[NormalizedRecord] = []
    for idx, row in enumerate(rows, start=2):
        if not should_include_global_payments_row(row):
            continue
        normalized.append(
            NormalizedRecord(
                source_system="global_payments",
                source_row_number=idx,
                card_brand=normalize_brand(resolve_field(row, "global_payments", "card_brand")),
                authorization_code=resolve_field(row, "global_payments", "authorization_code"),
                amount=normalize_amount(resolve_field(row, "global_payments", "amount")),
                batch_control=resolve_field(row, "global_payments", "batch_control"),
                transaction_date=resolve_field(row, "global_payments", "transaction_date"),
                card_last4=extract_card_last4(resolve_field(row, "global_payments", "card_number")),
            )
        )
    return normalized


def normalize_versapay(rows: Iterable[dict[str, object]]) -> list[NormalizedRecord]:
    normalized: list[NormalizedRecord] = []
    for idx, row in enumerate(rows, start=2):
        tx_type = resolve_field(row, "versapay", "transaction_type").lower()
        if tx_type != "settle":
            continue
        normalized.append(
            NormalizedRecord(
                source_system="versapay",
                source_row_number=idx,
                card_brand=normalize_brand(resolve_field(row, "versapay", "card_brand")),
                authorization_code=resolve_field(row, "versapay", "authorization_code"),
                amount=normalize_amount(resolve_field(row, "versapay", "amount")),
                batch_control=resolve_field(row, "versapay", "batch_control"),
                source_batch_id=resolve_field(row, "versapay", "batch_control"),
                transaction_type=tx_type,
                card_last4=extract_card_last4(resolve_field(row, "versapay", "card_number")),
            )
        )
    return normalized
