# Plugin store and update indexes

CheeseSec Plugins is an independent plugin product for the CheeseSec ecosystem. Check each plugin's documentation and the host product's documentation for supported products, compatible versions, and installation steps.

## Browse plugins

The [CheeseSec plugin store](https://store.cheesesec.com/) is available without signing in. It displays published plugins. An empty catalog means there are no formal releases to display; documentation examples are not installable plugins.

Developers can also read the public v1 catalog:

```sh
curl --fail https://store.cheesesec.com/v1/catalog/index.json
```

The catalog contains publication records, withdrawals, and a catalog sequence. Readers should recognize `api_version` and check record types, namespaces, versions, and digests. A withdrawn release should not remain an installation candidate.

## Update indexes

Public update indexes distinguish the `stable`, `canary`, and `dev` channels:

```text
https://ota.cheesesec.com/v1/channels/stable/index.json
https://ota.cheesesec.com/v1/channels/canary/index.json
https://ota.cheesesec.com/v1/channels/dev/index.json
```

A channel index may contain no releases. The presence of an index does not mean that every host supports automatic updates. First confirm the host product's upgrade support, compatibility requirements, and backup steps.

## Downloads and verification

Resource URLs in formal release records have this form:

```text
https://res.cheesesec.com/sha256/<sha256>/<filename>
```

Check the downloaded content against the release record's SHA-256 digest. A matching digest establishes content integrity; it does not replace signature, source trust, withdrawal, or compatibility checks. Install through the host product's supported verification and installation flow, and do not directly execute an unverified package.

## Public API conventions

- Public catalog, update index, and resource endpoints support `GET` and `HEAD` reads.
- Do not send passwords, session cookies, access tokens, or other credentials to public read endpoints.
- Unknown paths return `404`; unsupported methods return `405`.
- Clients can use `ETag` and conditional requests to avoid repeated downloads. Index sequences should prevent older indexes from being treated as newer ones.
- Resource downloads support a single byte range. Clients should handle `206` and `416` responses.

The corresponding v1 schemas define public JSON structures. See the [CRP development guide](crp-development.en.md) for package format details. Host integration examples apply only to their named products.
