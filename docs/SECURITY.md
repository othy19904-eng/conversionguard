# Security boundaries

The public pilot works from exports and requires no production credentials.

Principles:
- read-only first;
- no customer payment data is required;
- do not commit tokens, service-account JSON, exports, or merchant data;
- use environment variables for credentials in later integrations;
- no automatic production mutation;
- no auto-merge or auto-deploy;
- staging/reproduction must be isolated from production.

The repository ignores common environment, database, IDE and test-artifact files by default.
