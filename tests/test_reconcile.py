from conversionguard.reconcile import reconcile_orders


def test_reconcile_finds_missing_duplicate_orphan_and_mismatch():
    orders = [
        {"transaction_id": "1001", "value": "20", "currency": "USD"},
        {"transaction_id": "1002", "value": "30", "currency": "USD"},
    ]
    conversions = [
        {"transaction_id": "1001", "value": "19", "currency": "USD"},
        {"transaction_id": "1001", "value": "19", "currency": "USD"},
        {"transaction_id": "9999", "value": "40", "currency": "USD"},
    ]
    result = reconcile_orders(orders, conversions)
    assert result["summary"]["missing_conversions"] == 1
    assert result["summary"]["duplicate_conversion_ids"] == 1
    assert result["summary"]["orphan_conversions"] == 1
    assert result["summary"]["value_mismatches"] == 1
    assert result["revenue_exposure"]["missing_conversion_order_value"] == 30.0
    assert result["revenue_exposure"]["affected_order_value"] == 50.0


def test_shopify_alias_can_match_measured_transaction_id():
    orders = [
        {"transaction_id": "1001", "aliases": ["987654321"], "value": 55, "currency": "USD"}
    ]
    conversions = [{"transaction_id": "987654321", "value": 55, "currency": "USD"}]
    result = reconcile_orders(orders, conversions)
    assert result["summary"]["matched"] == 1
    assert result["summary"]["missing_conversions"] == 0


def test_aggregated_event_count_exposes_duplicate_signal():
    orders = [{"transaction_id": "1001", "value": 20, "currency": "USD"}]
    conversions = [{"transaction_id": "1001", "value": 20, "currency": "USD", "event_count": 2}]
    result = reconcile_orders(orders, conversions)
    assert result["summary"]["duplicate_conversion_ids"] == 1
