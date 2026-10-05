# Collection methodology

## Sources

- DNS: Google Public DNS JSON API, queried for A, AAAA, MX, NS, TXT, and CAA records. [API documentation](https://developers.google.com/speed/public-dns/docs/doh/json).
- Certificate names: crt.sh JSON domain query. [Upstream database and API implementation](https://github.com/crtsh/certwatch_db).

The requested domain is normalized to lowercase IDNA ASCII. CT names are accepted only when they equal that domain or end with a dot followed by that domain. Wildcards remain explicit: `*.example.com` is a certificate name pattern, not evidence that a particular host exists. Repeated names are combined, retaining returned certificate URLs. Certificate IDs in the offline fixture are invented.

DNS owner names are retained because a resolver may return records after following a CNAME. Address records are canonicalized; NS and MX hostnames are normalized. TXT and CAA content remains as returned. Only answers matching the requested record type are retained; this is not a full DNS packet archive or DNSSEC audit.

## Provenance

Each source includes its query URL, UTC request-start timestamp, status, and a SHA-256 digest of the response bytes when successfully received and decoded. Observations reference that source's ID. Fixture hashes use canonicalized fixture JSON, not network bytes. The report's mode makes that distinction explicit.

Hashes identify response bytes; they do not independently prove source authenticity, ownership, or a forensic chain of custody. Raw HTTP bodies are not retained by this MVP. Preserve raw evidence separately when your investigation requires independent replay or formal evidence handling.

## Errors and comparisons

DNS NXDOMAIN is recorded as DNS status 3 and a successful lookup with no requested records. SERVFAIL and other error codes, truncation, HTTP errors, rate limits, invalid payloads, and timeouts are recorded as failures. Responses larger than 10 MiB are rejected rather than silently truncated. The tool does not retry automatically.

Comparison requires the same domain, schema, and mode. It compares `(source, owner, value)` only for sources successful in both reports. Unavailable sources are listed as excluded. A change means an observation differs, not that a host was created or destroyed. Successful CT queries can still have incomplete coverage; disappearing names require investigation. No source guarantees exhaustive results.

## Interpretation

- A certificate name does not establish current DNS resolution, a live service, company ownership, or a vulnerability.
- A DNS answer is an observation from one resolver at a particular time; caching, geolocation, and split DNS can affect it.
- A shared IP or certificate relationship is an investigative lead, not attribution.
- Avoid numeric confidence scores without a defined calibration method. Label facts, corroborated interpretations, and unresolved questions explicitly.
