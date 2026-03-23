from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from .models import BatchReconRow, MatchResult, NormalizedRecord


def build_detail_key(record: NormalizedRecord) -> str:
    return f"{record.card_brand}|{record.authorization_code}|{record.amount.quantize(Decimal('0.01'))}"


def reconcile_detail(
    versapay_records: list[NormalizedRecord],
    gp_records: list[NormalizedRecord],
) -> list[MatchResult]:
    vp_map: dict[str, list[NormalizedRecord]] = defaultdict(list)
    gp_map: dict[str, list[NormalizedRecord]] = defaultdict(list)

    for record in versapay_records:
        vp_map[build_detail_key(record)].append(record)
    for record in gp_records:
        gp_map[build_detail_key(record)].append(record)

    keys = sorted(set(vp_map) | set(gp_map))
    return [
        MatchResult(
            key=key,
            versapay=tuple(vp_map.get(key, [])),
            global_payments=tuple(gp_map.get(key, [])),
        )
        for key in keys
    ]


def derive_batch_reconciliation(matches: list[MatchResult]) -> list[BatchReconRow]:
    buckets: dict[tuple[str, str], dict[str, Decimal | int]] = {}

    for match in matches:
        if not match.global_payments:
            continue
        gp_brand = match.global_payments[0].card_brand
        gp_batch = match.global_payments[0].batch_control
        bucket_key = (gp_brand, gp_batch)
        if bucket_key not in buckets:
            buckets[bucket_key] = {
                "gp_count": 0,
                "gp_amount": Decimal("0"),
                "vp_count": 0,
                "vp_amount": Decimal("0"),
            }

        bucket = buckets[bucket_key]
        bucket["gp_count"] += len(match.global_payments)
        bucket["gp_amount"] += sum((r.amount for r in match.global_payments), Decimal("0"))
        bucket["vp_count"] += len(match.versapay)
        bucket["vp_amount"] += sum((r.amount for r in match.versapay), Decimal("0"))

    return [
        BatchReconRow(
            card_brand=brand,
            gp_batch_control=batch_control,
            gp_count=int(values["gp_count"]),
            gp_amount=Decimal(values["gp_amount"]),
            matched_versapay_count=int(values["vp_count"]),
            matched_versapay_amount=Decimal(values["vp_amount"]),
        )
        for (brand, batch_control), values in sorted(buckets.items())
    ]
