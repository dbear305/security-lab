# Domain evidence: example.com

Collected: 2026-10-04T16:08:18.204910Z
Mode: synthetic_fixture
All configured source requests succeeded: True

Collection success does not imply exhaustive coverage. Certificate names do not prove live hosts, ownership, or vulnerabilities.

## Sources

| Source | Status | URL | Detail |
| --- | --- | --- | --- |
| dns:A | ok | https://dns.google/resolve?name=example.com&amp;type=A | DNS status 0 |
| dns:AAAA | ok | https://dns.google/resolve?name=example.com&amp;type=AAAA | DNS status 0 |
| dns:MX | ok | https://dns.google/resolve?name=example.com&amp;type=MX | DNS status 0 |
| dns:NS | ok | https://dns.google/resolve?name=example.com&amp;type=NS | DNS status 0 |
| dns:TXT | ok | https://dns.google/resolve?name=example.com&amp;type=TXT | DNS status 0 |
| dns:CAA | ok | https://dns.google/resolve?name=example.com&amp;type=CAA | DNS status 0 |
| ct | ok | https://crt.sh/?q=%25.example.com&amp;output=json | Collected |

## Observations

| Source | Owner | Value |
| --- | --- | --- |
| dns:A | example.com | 192.0.2.10 |
| dns:AAAA | example.com | 2001:db8::10 |
| dns:MX | example.com | 10 mail.example.com |
| dns:NS | example.com | ns1.example.com |
| dns:TXT | example.com | &quot;v=spf1 -all&quot; |
| dns:CAA | example.com | 0 issue &quot;ca.example&quot; |
| ct |  | *.example.com |
| ct |  | example.com |
| ct |  | www.example.com |
