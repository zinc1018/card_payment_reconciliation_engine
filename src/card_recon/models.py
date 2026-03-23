from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class NormalizedRecord:
    source_system: str
    source_row_number: int
    card_brand: str
    authorization_code: str
    amount: Decimal
    batch_control: str = ""
    transaction_date: str = ""
    source_batch_id: str = ""
    transaction_type: str = ""


@dataclass(frozen=True)
class MatchResult:
    key: str
    versapay: tuple[NormalizedRecord, ...]
    global_payments: tuple[NormalizedRecord, ...]


@dataclass(frozen=True)
class BatchReconRow:
    card_brand: str
    gp_batch_control: str
    gp_count: int
    gp_amount: Decimal
    matched_versapay_count: int
    matched_versapay_amount: Decimal
