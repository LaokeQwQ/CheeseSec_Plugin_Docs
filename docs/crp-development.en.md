# CRP Development Handbook (Contract)

This page separates the executable CRP v1 format from future extensions. Do not
put planned fields in a v1 package or use them as a current Get Started step
until the corresponding parser, tests, and stage evidence exist.

## Executable v1 archive layout

`CheeseWAF/internal/crp.ParseArchive` currently accepts exactly three logical
entry types in the ZIP archive:

| Path | Requirement |
|---|---|
| `manifest.json` | exactly one strict JSON document |
| `artifact/<file>` | exactly one regular file; `artifact.name` may constrain its basename |
| `signatures/manifest.json` | exactly one JSON array |

The parser rejects unknown entries, `provenance/`, directories, symlinks,
duplicate paths, traversal paths, and entries over the configured size limits.
`provenance/` is not part of v1. Keep source evidence, SBOMs, or build records
as external evidence, or wait for the v2 contract.

### v1 manifest fields

The manifest uses `crp.cheesewaf.io/v1`. The current parser accepts these fields:

| Field | Rule |
|---|---|
| `api_version` | optional; when present, must be `crp.cheesewaf.io/v1` |
| `kind` | optional; when present, must be `CheeseWAFResourcePackage` |
| `name`, `plugin_id` | at least one is required; producers should keep both consistent |
| `version` | required SemVer text |
| `namespace` | must use a supported form such as `official/<plugin>` or `enterprise/<org>/<plugin>` |
| `publisher` | optional publisher identifier |
| `source` | optional for syntax-only parsing; `Import` requires a registered source |
| `source_root` | required stable source-root identifier |
| `release_sequence` | numeric; an initial package may use `0`, but a non-zero installed sequence cannot be replaced by `0` |
| `digests` | top-level compatibility field, or `artifact.digests`; if both are present they must match exactly |
| `artifact` | optional object; when present, its `name`, `size`, and `digests` are checked; digests may also be top-level |
| `artifact.name` | optional artifact basename constraint |
| `artifact.size` | optional in standalone validation; required to match the archive file size |
| `artifact.digests` | lowercase hexadecimal MD5, SHA-1, and SHA-256 values |

MD5 and SHA-1 are transport-integrity and resume checks only. SHA-256 is the
content identity. Missing or mismatched digests are hard failures and cannot be
overridden by an administrator.

`signatures/manifest.json` contains the current `Signature` fields: `key_id`,
`algorithm`, `value`, and optional `signed_at`. The empty array in the example
only proves archive layout; it does not pass `Import`, which still requires a
valid trust root and signature threshold.

See the minimal parseable, non-installable example in
[`examples/crp-v1/`](../examples/crp-v1/).

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

An unknown root or key, a revoked or expired key, a bad signature, or an
unmet threshold is always rejected by current v1. A registered community,
personal, test, development, or untrusted root returns `needs_confirmation`.
When an upper-layer UI or CLI permits continuation, it must show the warning,
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

## v2 and extension planning

The following are not v1 manifest fields and must not appear in the current Get
Started example:

- `package_id`, `class`, target CheeseWAF/extension API, platform/architecture,
  minimum audit-event version, and permission declarations;
- a `provenance/` directory containing SBOMs, build records, or publisher statements;
- DuckDB-specific fields, host-version matrices, and analysis-data constraints.

These items require a new schema, parser, signature coverage, migration notes,
and regression tests. Until then, keep them in the planned v2 or DuckDB contract
and do not describe them as current runtime behavior.
