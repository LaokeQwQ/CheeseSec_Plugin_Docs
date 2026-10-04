# Cloudflare Edge Routing Contract (v1)

This document fixes the split between CheeseSec public read surfaces and the CheeseWAF server. It is a publication and routing contract. It does not claim that production domains, R2 buckets, Cloudflare Tunnel, or Access policies are configured.

## Request split

The following domains are public read-only surfaces. They accept only `GET` and `HEAD`, receive no plugin credentials, and never forward unknown paths to the server.

| Domain | Allowed paths | R2 object prefix | Cache class |
|---|---|---|---|
| `store.cheesesec.com` | `/v1/catalog/index.json`, `/v1/policy/*.json`, `/v1/schema/{store,crp}/*.schema.json` | `catalog/`, `policy/`, `schema/` | short revalidation |
| `ota.cheesesec.com` | `/v1/channels/{stable,canary,dev}/index.json` | `ota/channels/` | short revalidation |
| `res.cheesesec.com` | `/sha256/{64 lowercase SHA-256}/{filename}` | `resources/sha256/` | long immutable |

The Worker reads R2 only through the fixed Host, path, and object-key mapping. An unknown Host returns `421`. An unknown path on a known public Host returns `404` and is not proxied. `POST`, `PUT`, `PATCH`, `DELETE`, and `OPTIONS` return `405` with `Allow: GET, HEAD`.

`res.cheesesec.com` supports one byte-range request. The Worker passes a valid `Range` to R2 and returns `206` or `416`. It does not read a complete CRP into Worker memory or recompute a large digest at the edge.

## Server requests

The following requests are pinned to `origin-admin.cheesesec.com`:

- Console pages, login, setup, and console assets on `console.cheesesec.com`.
- `/api/...`, `/health/ready`, `/health/cluster`, and other registered management endpoints on `api.cheesesec.com`.
- Authentication, sessions, CSRF, RBAC, approvals, CRP import and activation, CWEDP negotiation, diagnostic uploads, SSE, and WebSocket traffic.

The Worker may construct an upstream URL only from the configured `ORIGIN_BASE_URL`. It removes client-supplied `X-Forwarded-*`, `X-CheeseSec-Edge-*`, `CF-Access-*`, and hop-by-hop headers, then adds a request ID, UTC timestamp, policy version, and HMAC envelope. Cloudflare Access service identity values are injected only from Worker Secrets. After HMAC verification, the server still performs its normal Session, CSRF, RBAC, and audit checks.

The server keeps `admin_listen` on loopback and keeps `admin_public: false`. The Tunnel maps `origin-admin.cheesesec.com` to `https://127.0.0.1:9443`; it must not target the public data-plane listener or a public IP.

## Publication objects and pointers

The publication repository creates versioned objects. The Worker reads current pointers only:

```text
indexes/catalog/seq-<20 decimal digits>.json
indexes/ota/<channel>/seq-<20 decimal digits>.json
indexes/policy/seq-<20 decimal digits>/<name>.json
resources/sha256/<sha256>/<filename>
pointers/catalog.json
pointers/ota/<channel>.json
```

The public mapping uses these fixed keys:

```text
catalog/index.json
policy/endpoints.json
policy/trust-roots.json
policy/source-registry.json
policy/revocations.json
schema/store-v1/<name>.schema.json
schema/crp-v1/<name>.schema.json
ota/channels/<channel>/index.json
```

Index sequences can only increase. Old indexes, resources, and withdrawal events cannot be overwritten or deleted. The Worker returns `ETag`, `Last-Modified` when available, `X-CheeseSec-Index-Sequence`, and the route-specific `Cache-Control`. It does not verify or re-sign CRP. CheeseWAF remains responsible for signature thresholds, source roots, revocation, downgrade protection, and activation.

## Configuration and release conditions

The Worker uses the fixed R2 bindings `PUBLICATION_INDEX` and `PUBLIC_RESOURCES`. `EDGE_POLICY_VERSION` and `ORIGIN_BASE_URL` may be non-sensitive variables. `EDGE_ORIGIN_HMAC`, `CF_ACCESS_CLIENT_ID`, and `CF_ACCESS_CLIENT_SECRET` must be Wrangler Secrets. Production repositories must not contain `.dev.vars`, Tunnel tokens, Access credentials, service tokens, or signing private keys.

Before release, record separate evidence for:

1. Pages static build, TypeScript, unit tests, and artifact-boundary checks.
2. Signed catalog, policy, schema, OTA indexes, and content-addressed resources in the R2 staging buckets.
3. Tunnel, Access ACL, Origin HMAC, and loopback admin-port checks.
4. Public `404`, `405`, `421`, conditional requests, range requests, and no-redirect checks.
5. Server `/health/ready`, authentication, approvals, audit, SSE, and WebSocket checks.

Until this evidence exists, store, OTA, and resource domains may be described only as contract examples, not as live services.
