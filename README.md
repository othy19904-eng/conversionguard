# ConversionGuard

**Catch broken ecommerce purchase measurement by reconciling analytics against real order truth.**

ConversionGuard is a read-only-first measurement integrity auditor for ecommerce teams. The public pilot edition takes two exports — authoritative orders and measured purchases — then finds transactions that are missing, duplicated, orphaned, or carrying the wrong value/currency.

## Why this exists

A store can keep taking orders while measurement quietly degrades. That can distort attribution, bidding and reporting without creating an obvious checkout outage.

ConversionGuard starts with a simpler question:

> Which real orders are represented correctly in measurement, which are not, and how much authoritative order value is touched by the defect?

**Measurement exposure is not claimed lost revenue.**

## 60-second demo

Requires Python 3.11+.

```bash
git clone https://github.com/othy19904-eng/conversionguard.git
cd conversionguard
python -m pip install -e .

conversionguard \
  --orders examples/demo/orders.csv \
  --conversions examples/demo/conversions.csv \
  --out examples/demo/demo-audit
```

The synthetic demo produces:

```text
Orders: 10
Matched: 8
Missing conversions: 2
Duplicate conversion IDs: 1
Value mismatches: 1
Currency mismatches: 1
Affected authoritative value: 493.00 USD
```

See [the generated demo report](examples/demo/demo-audit.md).

## What the public pilot detects

- missing purchase conversions;
- duplicate transaction IDs;
- conversions with no matching authoritative order;
- order/conversion value mismatches;
- currency mismatches;
- Shopify/order aliases for matching alternate transaction IDs;
- measurement exposure based on authoritative order value.

Inputs can be CSV or JSON.

## First-store pilot

No production credentials are required for the first audit. A merchant or agency can provide exports covering the same date window:

- orders: `transaction_id,value,currency`
- measured purchases: `transaction_id,value,currency`

**We are currently looking for 3 Shopify stores/agencies for the first real-world cohort.**

➡️ [Request a pilot / join the 3-store cohort](https://github.com/othy19904-eng/conversionguard/issues/1)

See [docs/PILOT.md](docs/PILOT.md) and [docs/SECURITY.md](docs/SECURITY.md).

## Product direction

The larger ConversionGuard prototype has explored continuous monitoring, raw-event forensics, change correlation and causal/recovery verification. **Those deeper layers are not claimed as part of this public pilot build yet.** The public repository is intentionally narrowed to the fastest real-market test: can the reconciliation audit produce evidence a store or agency values enough to keep using or pay for?

## Validation gate

Before building a dashboard, billing system, or adding more surface area:

- audit at least **3 real stores**;
- document onboarding friction and false positives;
- find at least one meaningful defect or confidently rule one out;
- get at least **1 merchant or agency willing to pay** for the audit or ongoing monitoring.

Until then: **pilot → evidence → payment**, not more features.

## Development

```bash
python -m pip install -e .
python -m pip install pytest
python -m pytest -q
```

CI runs on every push to `main` and every pull request.

## Status

Public pilot: **v0.1.0**.

The current public test suite covers reconciliation, alias matching and aggregated duplicate-event signals. Live Shopify/GA4/Google Ads integrations are deliberately not presented as validated in this public edition until they are tested on real merchant accounts.
