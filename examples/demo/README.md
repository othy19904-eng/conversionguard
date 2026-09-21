# Demo

This synthetic dataset intentionally contains:
- two missing measured purchases;
- one duplicated purchase;
- one value mismatch;
- one currency mismatch.

Run:

```bash
conversionguard --orders examples/demo/orders.csv --conversions examples/demo/conversions.csv --out examples/demo/demo-audit
```

The demo contains no merchant or customer data.
