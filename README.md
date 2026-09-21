# ConversionGuard

**Find broken ecommerce conversion tracking before it silently distorts ad decisions.**

ConversionGuard reconciles authoritative store orders with analytics/ads measurement, quantifies **measurement exposure**, monitors for regressions, and preserves an evidence chain from anomaly → likely change → mechanism → recovery.

It is designed first for **Shopify stores and agencies using GA4 / Google Ads**, with a read-only-first workflow.

## Why this exists

A store can keep taking orders while measurement breaks quietly:

- purchases disappear from GA4;
- the same transaction is sent twice;
- value or currency is wrong;
- a checkout/theme/GTM/deploy change introduces a regression;
- Ads reporting continues, but the measurement layer no longer represents store truth reliably.

ConversionGuard starts from the store's order ledger and asks: **which real orders are represented correctly in measurement, which are not, and what changed when the defect appeared?**

## 60-second offline demo

The demo uses synthetic CSV files and requires no Shopify, GA4, Ads, or GitHub credentials.

```bash
python -m pip install -e .
conversionguard \
  --orders examples/demo/orders.csv \
  --conversions examples/demo/conversions.csv \
  --out examples/demo/demo-audit
```

Expected demo result:

```text
Orders:                         10
Matched:                         8
Missing conversions:             2
Duplicate conversion IDs:        1
Value mismatches:                 1
Currency mismatches:              1
Affected authoritative value:  $493
```

The included generated report is at [`examples/demo/demo-audit.md`](examples/demo/demo-audit.md).

> **Important:** “measurement exposure” is not claimed lost revenue. It is authoritative order value touched by a measurement defect.

## What the current product can do

1. **Store ↔ analytics reconciliation** — compare Shopify/order exports with GA4 conversion records by transaction ID, value and currency.
2. **Daily integrity monitoring** — detect capture-rate drops, duplicates and other regressions against historical baselines.
3. **Raw-event forensics** — inspect GA4 BigQuery purchase events for missing IDs, duplicate patterns, stream/path shifts and value/currency inconsistencies.
4. **Change correlation** — correlate incident onset with GitHub deployments, Shopify theme changes and supplied GTM/config change logs.
5. **Causal evidence loop** — inspect exact diffs, verify recovery/rollback evidence, and optionally reproduce defects in isolated staging.
6. **Known-fix reuse** — recognize recurring causal signatures and prepare guarded repair runbooks.
7. **Human-controlled repair path** — generate a tested draft repair PR, independently gate merge readiness, then verify production recovery after a human merge/deploy.

ConversionGuard deliberately does **not** auto-merge, auto-deploy, roll back production, or execute production mutations.

## Start with the low-friction pilot

A first pilot does not need production credentials. A merchant or agency can provide two exports:

- authoritative orders (`transaction_id`, `value`, `currency`);
- measured purchase conversions with the same fields.

ConversionGuard returns a reconciliation report showing missing, duplicate, orphan, value/currency defects and affected order value. If the pilot finds a real issue, deeper read-only API and BigQuery monitoring can be enabled afterwards.

See [`docs/PILOT.md`](docs/PILOT.md) for the pilot workflow and [`docs/SECURITY.md`](docs/SECURITY.md) for access boundaries.

## Product status

**v1.9.1 productization build.** Core engine tests: **139 passing** in the packaged test suite. Live third-party integrations still need validation on real merchant accounts before making production reliability claims.

The detailed engineering history from v1.3–v1.9 is preserved in [`docs/TECHNICAL_HISTORY.md`](docs/TECHNICAL_HISTORY.md).

## Quick commands

Offline reconciliation:

```bash
conversionguard --orders orders.csv --conversions conversions.csv --out audit
```

Read-only Shopify + GA4 Data API reconciliation:

```bash
export SHOPIFY_ACCESS_TOKEN='...'
conversionguard \
  --shopify-shop your-store.myshopify.com \
  --ga4-property 123456789 \
  --days 7 \
  --out audit
```

For the advanced forensic/causal modes, see [`docs/TECHNICAL_HISTORY.md`](docs/TECHNICAL_HISTORY.md).

## Pilot success gate

Do **not** build a dashboard just because it is possible. The next product milestone is evidence from real stores:

- 3+ real stores audited;
- at least one material tracking defect detected or confidently ruled out;
- at least one merchant/agency willing to pay for the audit or ongoing monitoring;
- onboarding/access friction documented.

Until those conditions exist, the priority is **pilot → evidence → payment**, not more feature depth.
