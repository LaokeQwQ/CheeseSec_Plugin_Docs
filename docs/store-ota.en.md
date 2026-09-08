# Store and OTA Contract (v1, contract-only)

This handbook defines the CheeseSec catalog, OTA, resource endpoints, and plugin runtime boundary. It is an auditable publication contract, not a claim that online services or an installer are deployed. Machine-readable schemas live in CheeseSec_Plugin/schema/store-v1/ and are mirrored under https://store.cheesesec.com/schema/store/v1/.

## Three fixed endpoints

| Endpoint | Role | Methods | Key constraint |
|---|---|---|---|
| https://store.cheesesec.com | catalog | GET, HEAD | publishes reviewed release summaries only |
| https://ota.cheesesec.com | version index | GET, HEAD | pull-only, monotonically increasing index sequence |
| https://res.cheesesec.com | immutable resource | GET, HEAD | URL is bound to a SHA-256 content address; redirects denied |

Endpoints accept no plugin credentials. Online pulls require administrator password confirmation, a one-shot Socket Lease, and audit. Offline mode must make zero network requests.

## Trust levels

The six supported namespaces are official, enterprise, community, personal, test, and development. Trust level describes provenance and never grants runtime capability; capability is still controlled by the sidecar descriptor, resource limits, approval, and policy.

- Official and certified enterprise normal releases use 2-of-3 signatures; high-risk releases use 3-of-5. An enterprise root is restricted to enterprise/<org>/<plugin>.
- Community, personal, test, and development releases require administrator confirmation by default; maximum key lifetimes are 365, 365, 30, and 7 days.
- Official and enterprise keys have a maximum lifetime of 1095 days. Rotation and revocation retain old records and never overwrite publication history.

## Immutable release and withdrawal

Each release binds namespace@version#release_sequence, all three CRP digests, manifest/signature-set/descriptor/provenance digests, source root, review evidence, and the signature verification report. Published records are append-only: they cannot be rewritten, downgraded, or changed by a mirror. Withdrawal is an appended event with a reason and evidence digest; an OTA index must stop referencing a withdrawn release.

## Offline import

Offline import requires a local .crp, trust roots, a source registry, and a revocation snapshot. The order is: exact CRP three-entry layout, manifest/schema, artifact size plus MD5/SHA-1/SHA-256, source-root binding, signature threshold and validity, revocation and release sequence, then administrator confirmation where required. Any failure rejects installation and activation. Only a package that clears every gate can enter the CheeseWAF staged flow. An expired revocation snapshot keeps last-known-good running while blocking new installation, upgrade, and promotion.

## 34A sidecar and CWEDP

Plugins run as asynchronous sidecars. The first mode is observe, default egress=deny, and the allowed outputs are snapshots, hints, and health state; request handling never waits for plugin I/O. WASM and in-process native plugins are outside this contract.

CWEDP is the only executor for installation, upgrade, rollback, and cluster distribution. After HELLO/CAPABILITIES/DistributionIntent negotiation, a node may pull from OTA, an authorized seed, an authorized peer, or an offline CRP. Ansible only bootstraps the distribution agent; it cannot push or replace CRP. Transfers retain all three digests, a signed manifest, content-addressed chunks, and source independence/quarantine records.

These pages and fields are contract examples. Until CheeseWAF stage evidence exists, store, OTA, CWEDP, and plugin activation must not be described as live capabilities.
