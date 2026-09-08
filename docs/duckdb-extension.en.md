# DuckDB Analysis Extension Contract (Planned)

This contract maps to roadmap items 32C, 33B, and 34A+. It defines delivery boundaries and acceptance gates for an optional analysis extension. Until the CheeseWAF stage board has executable evidence, no capability below is shipped.

## Boundary and defaults

- DuckDB is for cross-cluster analysis and audit only, running as an optional sidecar or CLI. It is disabled and absent from the default CheeseWAF release.
- It never enters the request hot path, writes PG/native-raft/Redis, shares a writable DuckDB file, or exposes a listening or remote database service.
- Collectors asynchronously produce time-windowed Parquet snapshots. Analysis is read-only; failure, timeout, or crash cannot change data-plane decisions. Policy candidates are declarative snapshots or hints and still require core validation, compilation, canary, and atomic loading.
- External egress is denied by default. Online catalog/resource access requires a short-lived Socket Lease; offline verification uses local CRP, trust roots, and a cached revocation snapshot.

## CRP v1 boundary

The current CheeseWAF parser executes a three-entry CRP v1 archive: `manifest.json`,
exactly one regular `artifact/<file>`, and `signatures/manifest.json`. It rejects
unknown entries, directories, symlinks, duplicate paths, traversal paths, and
entries over the configured limits. `provenance/` is not part of v1 and must not
appear in the current Get Started example or current `.crp` package.

The v1 manifest uses only fields accepted by the current parser: `api_version`,
`kind`, `name`, `plugin_id`, `version`, `namespace`, `publisher`, `source`,
`source_root`, `release_sequence`, `digests`, and `artifact` (with optional
`name`, `size`, and `digests`). Unknown fields are rejected. All three digests
must be present and match; SHA-256 is the content identity, while MD5/SHA-1 are
transport-integrity and resume checks only.

See the minimal v1 archive example in [`../examples/crp-v1/`](../examples/crp-v1/).
It uses an empty signature array to demonstrate layout only; it cannot pass
`Import` or be installed.

## v2 and DuckDB extension planning

`package_id`, `class`, target CheeseWAF/extension API, platform/architecture,
minimum audit-event version, permission declarations, and a `provenance/`
directory are planned v2 additions, not current v1 fields. DuckDB-specific
fields, SBOMs, build records, and host-version matrices also require a new
schema, signature coverage, migration notes, and regression tests before they
can be added.

The following remain planned policy, not checks executed by the current v1
parser: a package should not carry a DuckDB executable, dynamic library,
container image, listening service, or production secret. If a host DuckDB is
needed later, the host must provide it as a separately controlled dependency
recorded in the compatibility matrix.

## Offline and online installation

Offline installation imports the .crp and revocation snapshot from trusted media, verifies all package/security/compatibility/audit gates, and shows the change list for confirmation. Import writes only staging; success creates a new control-plane revision, failure cleans staging. Stale revocation state is recorded; high-risk or expired state remains pending and cannot be forced active.

Online installation gets metadata only from the catalog and packages only from immutable resources, binding both to local digests. OTA proposes a candidate revision and cannot load it directly. Short leases, rate limits, resumable chunks, and the same full verification as offline mode apply. Mirrors cannot change identity, root, sequence, or permissions. Install, upgrade, and rollback retain digest, operator, confirmations, source, audit events, and result; rollback creates a new revision to a verified version.

## Signing roots and rotation

In the v2/extension plan, official and enterprise normal releases require at least 2-of-3 signatures and high-risk operations require 3-of-5. Enterprise roots are independent and cannot lower the platform minimum. Community, personal, test, and development roots require administrator confirmation by default; key lifetimes are capped at 1 year, 1 year, 30 days, and 7 days. Official/enterprise signing keys are capped at 3 years. Root certificate, key ID, purpose, validity, and revocation must be traceable in the planned manifest/provenance. Current v1 has none of these fields.

Root rotation is part of the v2/extension plan: use an old/new cross-signing window, publish new trust metadata signed by the old root, accept new-root packages during the window, then revoke the old root. Never overwrite the old record. Offline sites import a signed root-update package with administrator confirmation; if continuity cannot be proven, retain the old root and reject the package. Audit revocation, emergency suspension, and compromise response, with precise blocking by the planned package ID, source root, and key ID.

## Compatibility matrix and audit restrictions

| Dimension | Gate |
|---|---|
| CheeseWAF | version/commit range; incompatible packages rejected at staging |
| Extension API | e.g. duckdb-analysis/v1; only declared capabilities allowed |
| DuckDB | host-provided version range; CRP carries no binary |
| Platform | OS, architecture, runtime ABI; unlisted combinations cannot activate |
| Data | Parquet schema, audit-event version, timezone, compression constraints |
| Security | capabilities, egress policy, Socket Lease, audit fields, rollback level |

The extension reads only minimized/redacted Parquet snapshots. It must not read raw request bodies, cookies, Authorization headers, tokens, keys, administrator sessions, or PG/Redis/native-raft. Queries require resource limits, timeout, cancellation, and result-size limits. Results are append-only audit records and cannot modify fact logs. Recommendations, availability signals, and alerts are observational outputs; they cannot weaken protocol/security floors, administrator hard rules, or core controls.

## Acceptance status

These documents are planning and contract drafts. They do not mean that the DuckDB extension, installer, OTA, CWEDP pull, or hot loading is implemented, released, or supported. Before launch, add executable evidence for offline/online installation, root rotation drills, compatibility tests, audit integrity, and rollback on the CheeseWAF stage board.
