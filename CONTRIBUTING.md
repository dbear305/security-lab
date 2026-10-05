# Contributing

Keep changes small and tied to a reproducible problem. Describe the current behavior, proposed change, sample output, and how it was verified.

1. Place new collectors and helpers under `src/`.
2. Include deterministic fixtures and meaningful tests for parsing, source failures, and interpretation risks.
3. Run `python3 -m unittest discover -s tests -v` from this directory.
4. Update the quick start or methodology when behavior changes.
5. Open a pull request with the test result and any limitations.

CI must work offline without API keys. Do not commit generated private reports, credentials, or third-party material without permission to redistribute it. New collectors should document provider limits and avoid silent retries or unbounded requests. Keep active-testing capabilities explicit and separate from source collection.

The MIT license covers this project; upstream dependencies and source data retain their own terms. Repository security issues should follow [SECURITY.md](SECURITY.md).

## Toolkit and lab updates

Edit `toolkit/catalog.json` for catalog changes, then regenerate the reference from the repository root:

```bash
python3 src/toolkit.py list --markdown > toolkit/README.md
python3 -m unittest discover -s tests -v
```

Keep upstream URLs, data exposure, setup estimates, and limitations explicit. Do not label a linked project audited or runtime-tested without evidence. Record actual versions and observations in lab write-ups. Do not commit raw case files or binaries.
