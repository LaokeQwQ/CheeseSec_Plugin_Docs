# CRP Development Handbook (Contract)

## Package layout

A CRP is an offline-verifiable `.crp` bundle containing at least
`manifest.json`, `artifact/`, `signatures/`, and `provenance/`. The manifest uses
`crp.cheesewaf.io/v1` and declares the plugin identity, SemVer, namespace,
source root, release sequence, size, and all three transfer digests.

MD5 and SHA-1 are transport-integrity checks for resume support. SHA-256 is the
content identity. Missing or mismatched digests are hard failures and cannot be
overridden by an administrator.

## Namespace and signatures

- Official: `official/<plugin>`;
- Enterprise: `enterprise/<org>/<plugin>`;
- Other classes: `<class>/<publisher>/<plugin>`.

Source roots, signers, and transport sources are verified separately. Official
and enterprise packages use at least 2-of-3 for normal releases and 3-of-5 for
high-risk operations. Enterprise roots are independent and cannot lower the
platform minimum. Community, personal, test, and development roots require
administrator confirmation by default and do not grant high privilege. Key
lifetimes are capped at 1 year, 1 year, 30 days, and 7 days respectively;
official and enterprise keys are capped at 3 years.

Unknown, community, personal, test, or untrusted signatures cannot silently
enable high-risk capabilities. If policy permits continuing, show the warning,
wait 10 seconds, collect password plus second and third confirmations, and
write the decision to the audit log.

## Runtime and release

Plugins run as sidecars and use asynchronous interfaces. They must not block a
WAF request thread or access secrets, tokens, cookies, Authorization headers,
administrator sessions, or raw request bodies. External egress is denied by
default; temporary connectivity requires a short-lived Socket Lease.

Release order is `build → test → sign → publish → observe → staged → canary → promote`.
Rollback creates a new control-plane revision; it does not replay an old package.
CheeseWAF must record executable evidence for installation, OTA, CWEDP, and hot
loading before this handbook describes those capabilities as available.
