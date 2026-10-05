# Lab 01: Evidence collection and reliable change detection

## Objective

Run a complete investigation workflow offline and distinguish a changed DNS observation from unavailable evidence. Python 3.10+ is the only prerequisite. All data is synthetic.

## Procedure

From the repository root:

```bash
python3 src/evidence.py example.com --fixture examples/fixture.json
```

Save the printed directory path. Inspect its JSON: there should be seven successful sources and the CT names `*.example.com`, `example.com`, and `www.example.com`. Out-of-scope names from the fixture must be absent. `www.example.com` should retain two certificate references.

Create a modified fixture in the ignored reports directory:

```bash
python3 -c "import json,pathlib; p=json.loads(pathlib.Path('examples/fixture.json').read_text()); p['responses']['dns:A']['Answer'][0]['data']='192.0.2.20'; del p['responses']['ct']; pathlib.Path('reports/changed-fixture.json').write_text(json.dumps(p))"
```

Compare, substituting the first run's actual path:

```bash
python3 src/evidence.py example.com --fixture reports/changed-fixture.json --previous reports/REPLACE_WITH_PRIOR_RUN/report.json
```

## Expected evidence

- Exit code 2 indicates partial collection, with both reports still saved.
- DNS A observation `192.0.2.10` is removed; `192.0.2.20` is added.
- CT is marked failed and excluded from comparison.
- No certificate-name removals are claimed because CT was unavailable.

## Interpretation and remediation

The synthetic DNS observation changed; the lab proves the comparison detects that change. It does not establish a live infrastructure change. For a real unexpected DNS change, corroborate against an authorized inventory and DNS control-plane history before recommending a correction. For CT failure, restore source availability and collect again before making claims about certificate names.

## Record the work

Use the [research template](../research/TEMPLATE.md). Include both report paths, the fixture change, exit status, and the limits of the conclusion. Delete the generated directories when finished if no longer needed.
