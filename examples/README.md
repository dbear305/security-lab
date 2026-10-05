# Synthetic examples

`fixture.json` contains invented DNS responses and certificate entries for `example.com`, including duplicate and out-of-scope names. Documentation-range addresses are intentional. Certificate IDs are illustrative and are not evidence about real certificates.

`report.json` and `report.md` were generated from this fixture. Their timestamps reflect demo execution, not live observation. Re-run from the repository root:

```bash
python3 src/evidence.py example.com --fixture examples/fixture.json
```

Live reports belong in the ignored `reports/` directory until reviewed and sanitized for publication.
