# Demonstration: certificate names are evidence, not live hosts

Status: reproducible synthetic demonstration. No live investigation or vulnerability claim.

## Question

Can the collector normalize duplicate certificate names, reject lookalike domains, and preserve uncertainty when a source fails?

## Method and evidence

Run the commands in [Lab 01](../labs/01-domain-evidence.md) with the committed [fixture](../examples/fixture.json). The [sample report](../examples/report.json) records the normalized output and source hashes.

The fixture contains `WWW.EXAMPLE.COM`, `www.example.com`, `*.example.com`, `notexample.com`, and `example.com.attacker.test`.

## Findings

The two differently cased `www` entries combine into one observation with two certificate references. The wildcard remains a wildcard. Both lookalike domains fall outside the requested domain boundary and are excluded. When CT is missing from the second fixture, the source is excluded from comparison rather than interpreted as evidence that its names disappeared.

## Limits and next verification

These results demonstrate parsing and error handling against synthetic inputs. They say nothing about the live configuration of example.com. Real host availability, attribution, and vulnerabilities require separate corroboration. Automated tests cover the demonstrated behaviors.
