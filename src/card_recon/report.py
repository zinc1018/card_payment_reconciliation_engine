from __future__ import annotations

from .models import BatchReconRow, MatchResult


def summarize_matches(matches: list[MatchResult]) -> dict[str, int]:
    return {
        "total_keys": len(matches),
        "matched_keys": sum(1 for item in matches if item.versapay and item.global_payments),
        "versapay_only_keys": sum(1 for item in matches if item.versapay and not item.global_payments),
        "gp_only_keys": sum(1 for item in matches if item.global_payments and not item.versapay),
    }


def summarize_batch_rows(rows: list[BatchReconRow]) -> dict[str, int]:
    return {
        "total_batches": len(rows),
        "balanced_batches": sum(
            1 for row in rows if row.gp_count == row.matched_versapay_count and row.gp_amount == row.matched_versapay_amount
        ),
    }
