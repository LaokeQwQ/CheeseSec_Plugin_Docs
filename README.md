# CheeseSec Plugin Handbook

This handbook defines the plugin catalog, CRP package, signing, review,
release, and operations contracts used by CheeseWAF. It is maintained with
the same verification standard as code. An example is either executable or
explicitly marked as a contract example.

Authoritative runtime contract: `CheeseWAF/docs/architecture/crp-contract.md`.

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
