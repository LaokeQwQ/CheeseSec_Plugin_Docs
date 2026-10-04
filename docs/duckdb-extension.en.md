# DuckDB Analysis Extension Contract (Planned)

This contract maps to roadmap items 32C, 33B, and 34A+. It defines delivery boundaries and acceptance gates for an optional analysis extension. Until the CheeseWAF stage board has executable evidence, no capability below is shipped.

## Boundary and defaults

- The DuckDB extension uses a `host-provided` asynchronous `one-shot-job` contract: the host supplies a controlled DuckDB version, and each job exits when complete. It is not a persistent sidecar or a user-facing CLI for arbitrary SQL. This repository currently contains only schemas, descriptors, policy, and fixtures; CheeseWAF has no job launcher or audit exporter wired in, and the default release does not include DuckDB.
- It never enters the request hot path, writes PG/native-raft/Redis, shares a writable DuckDB file, or exposes a listening or remote database service.
- A job reads only redacted Parquet snapshots from a trusted exporter and uses a parameterized query template registered by this repository. It must not execute arbitrary user SQL. The host must verify input signatures, file digests and schema, and enforce an OS sandbox and resource limits around DuckDB; none of these runtime controls has implementation evidence yet.
- The only output is `analysis-record/v1`. Recommendations such as `contain` or `isolate` are analysis labels; they cannot become `risk-hint/v1`, policy candidates, ACLs, challenges, blocks, or policy updates.
- After core validation, the host signs the manifest and `analysis-record/v1` with the `cheesewaf-extension-output-attestation-v1` domain. The signature binds the canonical payload SHA-256, `key_id`, and UTC `signed_at`. Plugins, DuckDB jobs, and Parquet files never hold the host private key; failed validation is discarded and audited.
- DuckDB jobs deny network egress, request no Socket Lease, and do not access online catalogs or resource services.

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
It carries two verifiable official Ed25519 signatures for archive-layout and
signature-gate checks. It remains a contract fixture; it does not show a wired
plugin runtime or prove that installation or activation is available.

## v2 and runtime boundary

`package_id`, `class`, target CheeseWAF/extension API, platform/architecture,
minimum audit-event version, permission declarations, and a `provenance/`
directory are planned v2 additions, not current CRP v1 fields. The DuckDB
`one-shot-job` descriptor and `analysis-record/v1` schema are defined here, but
CheeseWAF has not wired an execution runtime. SBOMs, build records, and a formal
host-version matrix still require schema, signature coverage, migration notes,
and regression tests.

Extension packages must not carry a DuckDB executable, dynamic library,
container image, listening service, or production secret. The host supplies
DuckDB separately and records its version. The current CRP v1 parser checks
archive structure and payload digests, not the file type of an arbitrary
payload, so the extension publication gate must enforce this policy.

## Offline and online installation

The target offline installation flow imports the .crp and revocation snapshot from
trusted media, verifies all package/security/compatibility/audit gates, and shows
the change list for confirmation. Import writes only staging; success creates a new
control-plane revision, failure cleans staging. The current CheeseWAF code exposes
only the local RuntimeStore contract and does not wire this control-plane flow.
The separate [Standalone Control Runtime](https://docs.cheesesec.com/docs/cheesewaf/control-plane-runtime/)
page documents the current `cheesewaf-control` command and fail-closed boundary; it does not provide plugin installation or activation.
Stale revocation state is recorded; high-risk or expired state remains pending and
cannot be forced active.

The target online installation flow gets metadata only from the catalog and packages
only from immutable resources, binding both to local digests. OTA proposes a
candidate revision and cannot load it directly. Short leases, rate limits, resumable
chunks, and the same full verification as offline mode apply. Mirrors cannot change
identity, root, sequence, or permissions. Install, upgrade, and rollback retain
digest, operator, confirmations, source, audit events, and result; rollback creates
a new revision to a verified version. The current binary does not wire the catalog,
OTA, lease, or control-plane executor. The separate `cheesewaf-control` entry does not provide plugin installation or activation.

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
| Security | capabilities, deny egress, OS sandbox, audit fields, rollback level |

The extension reads only signature-verified and validated redacted Parquet snapshots. It must not read raw request bodies, cookies, Authorization headers, tokens, keys, administrator sessions, or PG/Redis/native-raft. Queries use a fixed template and have input-size, time, CPU, memory, temporary-space, and result-size limits; an OS sandbox isolates files, network, and process resources. The only output is a provenance-bound append-only `analysis-record/v1`; it cannot modify fact logs. Analysis labels, alerts, and risk rankings cannot weaken protocol/security floors, administrator hard rules, or core controls.

## Acceptance status

These documents define an extension contract; they do not mean that the DuckDB job runtime, audit exporter, installer, OTA, CWEDP pull, or hot loading is implemented, released, or supported. Current gates validate schemas, descriptors, fixtures, host-attestation fields, and static contracts. They do not prove runtime enforcement of input signatures, Parquet contents, SQL templates, host signature verification, or OS sandboxing. Before integration, add runtime gates, resource limits, and isolation tests to the CheeseWAF stage board.
