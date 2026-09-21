from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def markdown_report(result: dict[str, Any]) -> str:
    s = result["summary"]
    e = result["revenue_exposure"]
    lines = [
        "# ConversionGuard audit",
        "",
        "## Summary",
        "",
        f"- Orders: **{s['orders']}**",
        f"- Matched: **{s['matched']}**",
        f"- Missing conversions: **{s['missing_conversions']}**",
        f"- Duplicate conversion IDs: **{s['duplicate_conversion_ids']}**",
        f"- Orphan conversions: **{s['orphan_conversions']}**",
        f"- Value mismatches: **{s['value_mismatches']}**",
        f"- Currency mismatches: **{s['currency_mismatches']}**",
        f"- Affected authoritative order value: **{e['affected_order_value']:.2f} USD**",
        "",
        "> Measurement exposure is not proven lost revenue. It is authoritative order value touched by a measurement defect.",
        "",
    ]
    if result["missing_conversion_ids"]:
        lines += ["## Missing transaction IDs", "", *[f"- {x}" for x in result["missing_conversion_ids"]], ""]
    if result["duplicate_conversion_ids"]:
        lines += ["## Duplicate transaction IDs", "", *[f"- {x}" for x in result["duplicate_conversion_ids"]], ""]
    if result["orphan_conversion_ids"]:
        lines += ["## Orphan conversion IDs", "", *[f"- {x}" for x in result["orphan_conversion_ids"]], ""]
    return "\n".join(lines)


def write_reports(result: dict[str, Any], out_prefix: str | Path) -> tuple[Path, Path]:
    p = Path(out_prefix)
    p.parent.mkdir(parents=True, exist_ok=True)
    json_path = p.with_suffix(".json")
    md_path = p.with_suffix(".md")
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(result), encoding="utf-8")
    return json_path, md_path
