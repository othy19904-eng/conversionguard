from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ID_KEYS = ("transaction_id", "order_id", "id", "order_number", "transactionId")
VALUE_KEYS = ("value", "total", "revenue", "amount", "total_price")
CURRENCY_KEYS = ("currency", "currency_code", "presentment_currency")


def _first(record: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return None


def _normalize_id(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip().lstrip("#")


def _normalize_money(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return round(float(str(value).replace(",", "").strip()), 2)
    except (TypeError, ValueError):
        return None


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    aliases = record.get("aliases") or []
    if isinstance(aliases, str):
        aliases = [x.strip() for x in aliases.split("|") if x.strip()]
    normalized_aliases = []
    for alias in aliases:
        value = _normalize_id(alias)
        if value:
            normalized_aliases.append(value)
    return {
        "transaction_id": _normalize_id(_first(record, ID_KEYS)),
        "aliases": normalized_aliases,
        "value": _normalize_money(_first(record, VALUE_KEYS)),
        "currency": str(_first(record, CURRENCY_KEYS) or "").upper() or None,
        "event_count": int(record.get("event_count") or 1),
        "raw": record,
    }


def load_records(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if p.suffix.lower() == ".csv":
        with p.open(newline="", encoding="utf-8-sig") as fh:
            return [dict(row) for row in csv.DictReader(fh)]
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        if isinstance(data, dict):
            for key in ("orders", "conversions", "rows", "data"):
                value = data.get(key)
                if isinstance(value, list):
                    return [x for x in value if isinstance(x, dict)]
        raise ValueError(f"JSON file {p} must contain a list of records or a supported top-level array.")
    raise ValueError(f"Unsupported export format: {p.suffix}. Use CSV or JSON.")


def _exposure(
    orders_by_primary: dict[str, dict[str, Any]],
    missing: list[str],
    duplicate_ids: list[str],
    duplicate_to_order: dict[str, str],
    value_mismatches: list[dict[str, Any]],
    currency_mismatches: list[dict[str, Any]],
    orphan_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    affected: set[str] = set(missing)
    affected.update(duplicate_to_order.get(x, x) for x in duplicate_ids if duplicate_to_order.get(x))
    affected.update(x["transaction_id"] for x in value_mismatches)
    affected.update(x["transaction_id"] for x in currency_mismatches)

    def order_value(txn_id: str) -> float:
        return float((orders_by_primary.get(txn_id) or {}).get("value") or 0.0)

    missing_value = round(sum(order_value(x) for x in missing), 2)
    affected_value = round(sum(order_value(x) for x in affected), 2)
    mismatch_delta = round(
        sum(abs(float(x["order_value"]) - float(x["conversion_value"])) for x in value_mismatches),
        2,
    )
    orphan_reported_value = round(sum(float(x.get("value") or 0.0) for x in orphan_rows), 2)

    return {
        "affected_order_count": len(affected),
        "affected_order_value": affected_value,
        "missing_conversion_order_value": missing_value,
        "value_mismatch_absolute_delta": mismatch_delta,
        "orphan_reported_value": orphan_reported_value,
        "interpretation": (
            "Measurement exposure, not proven lost revenue. Affected order value counts authoritative "
            "order value for unique orders with a missing, duplicate, value, or currency issue."
        ),
    }


def reconcile_orders(
    orders: list[dict[str, Any]],
    conversions: list[dict[str, Any]],
    value_tolerance: float = 0.01,
) -> dict[str, Any]:
    norm_orders = [normalize_record(row) for row in orders]
    norm_conversions = [normalize_record(row) for row in conversions]

    orders_by_primary = {row["transaction_id"]: row for row in norm_orders if row["transaction_id"]}
    alias_to_primary: dict[str, str] = {}
    for primary, row in orders_by_primary.items():
        alias_to_primary[primary] = primary
        for alias in row.get("aliases") or []:
            alias_to_primary[alias] = primary

    conversion_ids: list[str] = []
    conversions_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in norm_conversions:
        txn_id = row["transaction_id"]
        if not txn_id:
            continue
        repeat = max(1, int(row.get("event_count") or 1))
        conversion_ids.extend([txn_id] * repeat)
        conversions_by_id.setdefault(txn_id, []).append(row)

    conversion_counts = Counter(conversion_ids)
    missing: list[str] = []
    value_mismatches: list[dict[str, Any]] = []
    currency_mismatches: list[dict[str, Any]] = []
    matched: list[str] = []

    for primary, order in orders_by_primary.items():
        candidate_ids = [primary] + list(order.get("aliases") or [])
        hits: list[tuple[str, dict[str, Any]]] = []
        for candidate in candidate_ids:
            for conversion in conversions_by_id.get(candidate, []):
                hits.append((candidate, conversion))
        if not hits:
            missing.append(primary)
            continue

        matched.append(primary)
        used_id, conversion = hits[0]

        if order["value"] is not None and conversion["value"] is not None:
            if abs(order["value"] - conversion["value"]) > value_tolerance:
                value_mismatches.append({
                    "transaction_id": primary,
                    "matched_conversion_id": used_id,
                    "order_value": order["value"],
                    "conversion_value": conversion["value"],
                })

        if order["currency"] and conversion["currency"] and order["currency"] != conversion["currency"]:
            currency_mismatches.append({
                "transaction_id": primary,
                "matched_conversion_id": used_id,
                "order_currency": order["currency"],
                "conversion_currency": conversion["currency"],
            })

    duplicate_ids = sorted([txn_id for txn_id, count in conversion_counts.items() if count > 1])
    duplicate_to_order = {txn_id: alias_to_primary.get(txn_id, "") for txn_id in duplicate_ids}
    orphan_ids = sorted([txn_id for txn_id in conversions_by_id if txn_id not in alias_to_primary])
    orphan_rows = [row for txn_id in orphan_ids for row in conversions_by_id.get(txn_id, [])]

    exposure = _exposure(
        orders_by_primary,
        missing,
        duplicate_ids,
        duplicate_to_order,
        value_mismatches,
        currency_mismatches,
        orphan_rows,
    )

    return {
        "summary": {
            "orders": len(norm_orders),
            "conversions": len(norm_conversions),
            "matched": len(matched),
            "missing_conversions": len(missing),
            "duplicate_conversion_ids": len(duplicate_ids),
            "orphan_conversions": len(orphan_ids),
            "value_mismatches": len(value_mismatches),
            "currency_mismatches": len(currency_mismatches),
            "orders_without_transaction_id": sum(1 for row in norm_orders if not row["transaction_id"]),
            "conversions_without_transaction_id": sum(1 for row in norm_conversions if not row["transaction_id"]),
        },
        "missing_conversion_ids": sorted(missing),
        "duplicate_conversion_ids": duplicate_ids,
        "orphan_conversion_ids": orphan_ids,
        "value_mismatches": value_mismatches,
        "currency_mismatches": currency_mismatches,
        "revenue_exposure": exposure,
    }
