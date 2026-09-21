from __future__ import annotations

import argparse

from .reconcile import load_records, reconcile_orders
from .report import write_reports


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="conversionguard",
        description="Audit ecommerce orders against measured purchase conversions.",
    )
    p.add_argument("--orders", required=True, help="Authoritative order export (.csv or .json)")
    p.add_argument("--conversions", required=True, help="Measured conversion export (.csv or .json)")
    p.add_argument("--out", default="conversionguard-audit", help="Output prefix")
    p.add_argument("--value-tolerance", type=float, default=0.01)
    return p


def main() -> int:
    args = build_parser().parse_args()
    orders = load_records(args.orders)
    conversions = load_records(args.conversions)
    result = reconcile_orders(orders, conversions, value_tolerance=args.value_tolerance)
    json_path, md_path = write_reports(result, args.out)

    s = result["summary"]
    e = result["revenue_exposure"]
    print(f"Orders: {s['orders']}")
    print(f"Matched: {s['matched']}")
    print(f"Missing conversions: {s['missing_conversions']}")
    print(f"Duplicate conversion IDs: {s['duplicate_conversion_ids']}")
    print(f"Value mismatches: {s['value_mismatches']}")
    print(f"Currency mismatches: {s['currency_mismatches']}")
    print(f"Affected authoritative value: {e['affected_order_value']:.2f} USD")
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
