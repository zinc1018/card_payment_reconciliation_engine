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


def normalize_global_payments(rows: Iterable[dict[str, object]]) -> list[NormalizedRecord]:
    normalized: list[NormalizedRecord] = []
    for idx, row in enumerate(rows, start=2):
        normalized.append(
            NormalizedRecord(
                source_system="global_payments",
                source_row_number=idx,
                card_brand=normalize_brand(resolve_field(row, "global_payments", "card_brand")),
                authorization_code=resolve_field(row, "global_payments", "authorization_code"),
                amount=normalize_amount(resolve_field(row, "global_payments", "amount")),
                batch_control=resolve_field(row, "global_payments", "batch_control"),
                transaction_date=resolve_field(row, "global_payments", "transaction_date"),
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
            )
        )
    return normalized
