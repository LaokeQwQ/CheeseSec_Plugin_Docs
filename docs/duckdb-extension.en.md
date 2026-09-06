# DuckDB Analysis Extension Contract (Planned)

This contract maps to roadmap items 32C, 33B, and 34A+. It defines delivery boundaries and acceptance gates for an optional analysis extension. Until the CheeseWAF stage board has executable evidence, no capability below is shipped.

## Boundary and defaults

- DuckDB is for cross-cluster analysis and audit only, running as an optional sidecar or CLI. It is disabled and absent from the default CheeseWAF release.
- It never enters the request hot path, writes PG/native-raft/Redis, shares a writable DuckDB file, or exposes a listening or remote database service.
- Collectors asynchronously produce time-windowed Parquet snapshots. Analysis is read-only; failure, timeout, or crash cannot change data-plane decisions. Policy candidates are declarative snapshots or hints and still require core validation, compilation, canary, and atomic loading.
- External egress is denied by default. Online catalog/resource access requires a short-lived Socket Lease; offline verification uses local CRP, trust roots, and a cached revocation snapshot.

## CRP resource package

An offline-verifiable .crp archive contains at least manifest.json, artifact/, signatures/, and provenance/. Artifact must not contain a DuckDB binary; provenance records source root, build record, SBOM digest, and publisher statement.

The crp.cheesewaf.io/v1 manifest declares package identity/class/namespace/publisher, SemVer, source_root, release_sequence, artifact_size, sha256, sha1, md5, target CheeseWAF/extension API, platform/architecture, minimum audit-event version, and permissions. SHA-256 is content identity; MD5/SHA-1 are transport/resume checks only. Missing or mismatched paths, sizes, digests, sequence, source root, or signatures are hard failures and cannot be overridden. Packages must not carry a DuckDB executable, dynamic library, container image, listening service, or production secret; a host-provided DuckDB is a separately controlled dependency in the matrix.

## Offline and online installation

Offline installation imports the .crp and revocation snapshot from trusted media, verifies all package/security/compatibility/audit gates, and shows the change list for confirmation. Import writes only staging; success creates a new control-plane revision, failure cleans staging. Stale revocation state is recorded; high-risk or expired state remains pending and cannot be forced active.

Online installation gets metadata only from the catalog and packages only from immutable resources, binding both to local digests. OTA proposes a candidate revision and cannot load it directly. Short leases, rate limits, resumable chunks, and the same full verification as offline mode apply. Mirrors cannot change identity, root, sequence, or permissions. Install, upgrade, and rollback retain digest, operator, confirmations, source, audit events, and result; rollback creates a new revision to a verified version.

## Signing roots and rotation

Official/enterprise normal releases require at least 2-of-3 signatures; high-risk operations require 3-of-5. Enterprise roots are independent and cannot lower the platform minimum. Community, personal, test, and development roots require administrator confirmation by default; key lifetimes are capped at 1 year, 1 year, 30 days, and 7 days. Official/enterprise signing keys are capped at 3 years. Root certificate, key ID, purpose, validity, and revocation must be traceable in manifest/provenance.

Use an old/new cross-signing window: publish new trust metadata signed by the old root, accept new-root packages during the window, then revoke the old root. Never overwrite the old record. Offline sites import a signed root-update package with administrator confirmation; if continuity cannot be proven, retain the old root and reject the package. Audit revocation, emergency suspension, and compromise response, with precise blocking by package ID, source root, and key ID.

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
