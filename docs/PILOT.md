# First-store pilot

The first pilot is deliberately low-friction and read-only.

## Input

Ask the merchant or agency for two exports covering the same date window:

1. authoritative orders: `transaction_id,value,currency`
2. measured purchase conversions: `transaction_id,value,currency`

CSV or JSON is accepted.

## Output

ConversionGuard reports:
- missing conversions;
- duplicate transaction IDs;
- orphan conversions;
- value mismatches;
- currency mismatches;
- affected authoritative order value.

**Affected order value is measurement exposure, not claimed lost revenue.**

## Success criteria

The pilot succeeds commercially only when it produces useful evidence for a real store and the buyer says the audit or continuous monitoring is worth paying for.

Do not request production write access for the first pilot.
