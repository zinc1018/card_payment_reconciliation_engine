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
            "Card Number": "411111XXXXXX1111",
        },
        {
            "Payment Method": "Visa",
            "Batch Control Number": "BATCH-1001",
            "Approval Code": "009999",
            "Original Transaction Amount": "23.45",
            "Process Date": "2025-09-01",
            "Card Number": "411111XXXXXX2222",
        },
    ]
    vp_rows = [
        {
            "type": "sale",
            "card brand": "Visa",
            "auth_code": "007313",
            "amount": "100.00",
            "batch_id": "",
            "account": "411111******1111",
        },
        {
            "type": "settle",
            "card brand": "Visa",
            "auth_code": "007313",
            "amount": "100.00",
            "batch_id": "VP-SETTLE-1001",
            "account": "411111******1111",
        },
        {
            "type": "settle",
            "card brand": "Visa",
            "auth_code": "009999",
            "amount": "23.45",
            "batch_id": "VP-SETTLE-1002",
            "account": "411111******2222",
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


def test_gp_adjustment_rows_are_excluded():
    gp_rows = [
        {
            "Payment Method": "AX",
            "Batch Control Number": "BATCH-2001",
            "Approval Code": "285115",
            "Original Transaction Amount": "2296.82",
            "Process Date": "2025-09-18",
            "Card Type": "30 - AMERICAN EXPRESS",
            "Charge Type": "1650",
        },
        {
            "Payment Method": "ADJ",
            "Batch Control Number": "BATCH-2002",
            "Approval Code": "285115",
            "Original Transaction Amount": "2296.82",
            "Process Date": "2025-09-18",
            "Card Type": "90 - ADJUSTMENTS",
            "Charge Type": "1901",
        },
    ]

    gp_records = normalize_global_payments(gp_rows)

    assert len(gp_records) == 1
    assert gp_records[0].batch_control == "BATCH-2001"
    assert gp_records[0].authorization_code == "285115"


def test_duplicate_auth_amount_is_disambiguated_by_card_last4():
    gp_rows = [
        {
            "Payment Method": "Visa",
            "Batch Control Number": "25254 T667",
            "Approval Code": "00618F",
            "Original Transaction Amount": "77.97",
            "Card Number": "453780XXXXXX4092",
        },
        {
            "Payment Method": "Visa",
            "Batch Control Number": "25256 T989",
            "Approval Code": "00618F",
            "Original Transaction Amount": "77.97",
            "Card Number": "452034XXXXXX6966",
        },
    ]
    vp_rows = [
        {
            "type": "settle",
            "card brand": "Visa",
            "auth_code": "00618F",
            "amount": "77.97",
            "batch_id": "834500885",
            "account": "453780******4092",
        },
        {
            "type": "settle",
            "card brand": "Visa",
            "auth_code": "00618F",
            "amount": "77.97",
            "batch_id": "835347876",
            "account": "452034******6966",
        },
    ]

    matches = reconcile_detail(normalize_versapay(vp_rows), normalize_global_payments(gp_rows))
    matched = [m for m in matches if m.versapay and m.global_payments]

    assert len(matched) == 2
    assert {m.key for m in matched} == {
        'Visa|00618F|77.97|4092',
        'Visa|00618F|77.97|6966',
    }


def test_batch_reconciliation_preserves_versapay_only_batch_control():
    gp_rows = []
    vp_rows = [
        {
            "type": "settle",
            "card brand": "Visa",
            "auth_code": "022156",
            "amount": "77.97",
            "batch_id": "830976351",
            "account": "411111******2500",
        }
    ]

    matches = reconcile_detail(normalize_versapay(vp_rows), normalize_global_payments(gp_rows))
    batch_rows = derive_batch_reconciliation(matches)

    assert len(batch_rows) == 1
    assert batch_rows[0].card_brand == 'Visa'
    assert batch_rows[0].gp_batch_control == '830976351'
    assert batch_rows[0].gp_count == 0
    assert batch_rows[0].gp_amount == Decimal('0')
    assert batch_rows[0].matched_versapay_count == 1
    assert batch_rows[0].matched_versapay_amount == Decimal('77.97')
