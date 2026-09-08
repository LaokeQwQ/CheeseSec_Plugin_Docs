# CheeseSec Plugin Handbook

This handbook defines the plugin catalog, CRP package, signing, review,
release, and operations contracts used by CheeseWAF. It is maintained with
the same verification standard as code. An example is either executable or
explicitly marked as a contract example.

Authoritative runtime contract: `CheeseWAF/docs/architecture/crp-contract.md`.

## Current CRP v1 quick check

The current code parses only three archive entries: `manifest.json`, one regular
`artifact/<file>`, and `signatures/manifest.json`. It rejects unknown entries,
so `provenance/` and extension-specific fields cannot appear in a current v1
package.

The v1 manifest uses `api_version`, `kind`, `name`, `plugin_id`, `version`,
`namespace`, `publisher`, `source`, `source_root`, `release_sequence`,
`digests`, and `artifact`. See the minimal archive in
[`examples/crp-v1/`](examples/crp-v1/). Its Chinese and English instructions
are `README.md` and `README.en.md`; it has no signature and cannot be installed.

| Function | Domain |
|---|---|
| Catalog | `store.cheesesec.com` |
| OTA indexes | `ota.cheesesec.com` |
| Immutable resources | `res.cheesesec.com` |

Package classes are `official`, `enterprise`, `community`, `personal`,
`test`, and `development`. Each class has a separate namespace and source
root. A mirror, peer, OTA endpoint, or Ansible bundle cannot change that
identity.

Runtime installation, OTA, and CWEDP pull are not claimed until CheeseWAF's
stage board records executable evidence.

`package_id`, `class`, target API, platform/architecture, permissions, SBOMs,
and `provenance/` are v2 or extension planning. They need a new schema, parser,
and regression tests before they enter Get Started.

## Optional DuckDB analysis extension

The DuckDB extension is a contract-only, optional sidecar/CLI plan for cross-cluster
analysis and audit. It is disabled and absent by default, does not enter the WAF request
path or state stores, and does not expose a network service.

See docs/duckdb-extension.md and docs/duckdb-extension.en.md. They define package layout,
offline/online delivery, signing-root rotation, compatibility gates, and audit restrictions.
They are not a claim that the extension is implemented or generally available.
