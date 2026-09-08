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
The mirrored publication schemas are in [`schema/crp-v1/`](schema/crp-v1/);
they validate shape and archive metadata, not signature trust or activation.

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

## Validation gate

The mirrored CRP v1 schemas are in `schema/crp-v1/`. The handbook CI validates
the schemas, every example manifest and signature set, artifact size/digests,
the exact three-entry archive layout, local Markdown links, and tracked-file
secret/release-artifact rules. Run the same checks locally:

```sh
python3 -m venv /tmp/cheesesec-plugin-docs-ci
/tmp/cheesesec-plugin-docs-ci/bin/pip install -r requirements-ci.txt
/tmp/cheesesec-plugin-docs-ci/bin/python scripts/check_workflow_policy.py
/tmp/cheesesec-plugin-docs-ci/bin/python scripts/validate_crp_v1.py
/tmp/cheesesec-plugin-docs-ci/bin/python scripts/secret_scan.py
git diff --check
```

The schema copy is kept byte-for-byte aligned with the publication repository's
canonical schema IDs. Validation dependencies and generated `.crp` files are
not runtime content and must not be committed.

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

## Store and OTA contract mirror

The bilingual store and OTA contract in docs/store-ota.md mirrors the publication
repository's machine-readable policies and schemas. policy/, catalog/, and ota/
are intentionally fail-closed with empty live indexes. The six trust levels,
immutable release records, append-only withdrawals, offline CRP inputs, 34A
sidecar descriptor, fixed endpoint policy, and CWEDP pull-only boundary are
validated by scripts/validate_commercial_contracts.py.

Run the mirror gate locally:

    python3 -m venv /tmp/cheesesec-plugin-docs-ci
    /tmp/cheesesec-plugin-docs-ci/bin/pip install -r requirements-ci.txt
    /tmp/cheesesec-plugin-docs-ci/bin/python scripts/validate_commercial_contracts.py
