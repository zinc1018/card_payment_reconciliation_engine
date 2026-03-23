from decimal import Decimal

from card_recon.match import derive_batch_reconciliation, reconcile_detail
from card_recon.normalize import normalize_global_payments, normalize_versapay
from card_recon.report import summarize_batch_rows, summarize_matches


def test_newer_gp_headers_and_versapay_settle_filter_work_together():
    gp_rows = [
        {
            "Payment Method": "Visa",
            "Batch Control Number": "BATCH-1001",
            "Approval Code": "007313",
            "Original Transaction Amount": "100.00",
            "Process Date": "2025-09-01",
        },
        {
            "Payment Method": "Visa",
            "Batch Control Number": "BATCH-1001",
            "Approval Code": "009999",
            "Original Transaction Amount": "23.45",
            "Process Date": "2025-09-01",
        },
    ]
    vp_rows = [
        {
            "type": "sale",
            "card brand": "Visa",
            "auth_code": "007313",
            "amount": "100.00",
            "batch_id": "",
        },
        {
            "type": "settle",
            "card brand": "Visa",
            "auth_code": "007313",
            "amount": "100.00",
            "batch_id": "VP-SETTLE-1001",
        },
        {
            "type": "settle",
            "card brand": "Visa",
            "auth_code": "009999",
            "amount": "23.45",
            "batch_id": "VP-SETTLE-1002",
        },
    ]

    gp_records = normalize_global_payments(gp_rows)
    vp_records = normalize_versapay(vp_rows)
    matches = reconcile_detail(vp_records, gp_records)
    batch_rows = derive_batch_reconciliation(matches)

    assert len(vp_records) == 2
    assert summarize_matches(matches) == {
        "total_keys": 2,
        "matched_keys": 2,
        "versapay_only_keys": 0,
        "gp_only_keys": 0,
    }
    assert len(batch_rows) == 1
    assert batch_rows[0].card_brand == "Visa"
    assert batch_rows[0].gp_batch_control == "BATCH-1001"
    assert batch_rows[0].gp_count == 2
    assert batch_rows[0].gp_amount == Decimal("123.45")
    assert batch_rows[0].matched_versapay_count == 2
    assert batch_rows[0].matched_versapay_amount == Decimal("123.45")
    assert summarize_batch_rows(batch_rows) == {
        "total_batches": 1,
        "balanced_batches": 1,
    }


def test_older_gp_headers_remain_supported():
    gp_rows = [
        {
            "Payment Method": "MC",
            "Batch Control Number": "999 T001",
            "Authorization Code": "052129",
            "Settlement Amount": "233.91",
            "Processing Date": "2025-08-31",
        }
    ]

    gp_records = normalize_global_payments(gp_rows)

    assert len(gp_records) == 1
    assert gp_records[0].card_brand == "MC"
    assert gp_records[0].authorization_code == "052129"
    assert gp_records[0].amount == Decimal("233.91")
    assert gp_records[0].transaction_date == "2025-08-31"
