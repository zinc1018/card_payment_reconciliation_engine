from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from .models import BatchReconRow, MatchResult, NormalizedRecord


def build_detail_key(record: NormalizedRecord) -> str:
    return f"{record.card_brand}|{record.authorization_code}|{record.amount.quantize(Decimal('0.01'))}|{record.card_last4}"


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
        gp_record = match.global_payments[0] if match.global_payments else None
        vp_record = match.versapay[0] if match.versapay else None
        brand = gp_record.card_brand if gp_record else vp_record.card_brand
        batch_control = gp_record.batch_control if gp_record and gp_record.batch_control else vp_record.batch_control
        if not batch_control:
            batch_control = 'UNASSIGNED'
        bucket_key = (brand, batch_control)
        if bucket_key not in buckets:
            buckets[bucket_key] = {
                'gp_count': 0,
                'gp_amount': Decimal('0'),
                'vp_count': 0,
                'vp_amount': Decimal('0'),
            }

        bucket = buckets[bucket_key]
        bucket['gp_count'] += len(match.global_payments)
        bucket['gp_amount'] += sum((r.amount for r in match.global_payments), Decimal('0'))
        bucket['vp_count'] += len(match.versapay)
        bucket['vp_amount'] += sum((r.amount for r in match.versapay), Decimal('0'))

    return [
        BatchReconRow(
            card_brand=brand,
            gp_batch_control=batch_control,
            gp_count=int(values['gp_count']),
            gp_amount=Decimal(values['gp_amount']),
            matched_versapay_count=int(values['vp_count']),
            matched_versapay_amount=Decimal(values['vp_amount']),
        )
        for (brand, batch_control), values in sorted(buckets.items())
    ]
