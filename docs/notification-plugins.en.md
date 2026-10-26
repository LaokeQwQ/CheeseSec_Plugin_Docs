# Notifier Provider Pack Contract

This page defines the boundary for a notifier provider pack. The short version:
a pack is a declarative descriptor. It describes how the CheeseWAF core notifier
delivers an alert to a destination. The core loads it from the local plugin
index, but a pack still carries no executable, has no network stack, holds no
credentials, and cannot enter the CRP install flow. Only the CheeseWAF core
delivers notifications.

## Compared with a sidecar

| Dimension | v1/v1.1 sidecar descriptor | notifier provider pack |
|---|---|---|
| Executable | asynchronous sidecar running code | no executable, image, WASM, or in-process module |
| Capabilities | `observe`, `candidate_snapshot`, `hint`, `health` | `alert_delivery`, `test_delivery`, contract labels only |
| Network | `egress` is fixed to `deny`; online access needs a short lease (not open yet) | no network stack; the core notifier resolves the target |
| Credentials | the plugin holds none | `secret_fields` holds reference names only; values stay in the core |
| Installation | handled by CWEDP/CRP (not live yet) | read from the local plugin index by the core; not executable, cannot enter CRP |
| Format | CRP manifest plus sidecar descriptor | standalone JSON contract `crp.cheesewaf.io/notifier/v1` |

v1.1 is still a planned extension of sidecar capabilities and has no `notify`
permission. A provider pack never means "the plugin can send notifications" or
"the plugin gained execution rights". The core loads the pack and the core
performs delivery.

## How packs are loaded

- The core scans `plugins.index_dir` (a relative path resolves against the data
  directory; the default is `<data-dir>/plugins`) for `*.json`. A missing
  directory is not an error; the service still starts.
- `plugins.watch_interval` controls how often the directory fingerprint is
  compared (default 2s, minimum 100ms, maximum 1h). Adding, removing, or editing
  a file rebuilds the index and swaps it atomically without a restart.
- A single broken file affects only that entry: it is reported and skipped while
  the rest of the index keeps loading.
- A pack whose `host_compatibility` range excludes the running host is not
  registered, and the reason is logged.
- A pack cannot shadow the six built-in types: the same configuration must not
  change meaning depending on which packs happen to be present.

## Why the core sends

Notification sends traffic outside the WAF. One layer must control the target,
redirects, private-network access, timeouts, retries, credential use, and audit.
Otherwise a plugin could bypass the core SSRF and private-endpoint policy.

- Plugins never hold host credentials and need no network stack; a provider pack
  only describes field shapes.
- Delivery must run asynchronously and must not block a WAF request thread.
- Offline mode still makes zero network requests; notifications do not retry on
  their own while offline.
- Failures, timeouts, and retries must be written to the core audit log. A pack
  does not carry retry logic.

## Contract fields

`schema/extensions-v1/notifier-provider.schema.json` uses
`additionalProperties: false`; strings, arrays, and templates all have bounds.
Fields that carry executable content (`executable`, `entrypoint`, `artifact`,
`command`, `wasm`, and similar) or declare their own egress (`egress`,
`egress_hosts`, and similar) are rejected by name rather than ignored.

| Field | Rule |
|---|---|
| `api_version` | fixed to `crp.cheesewaf.io/notifier/v1` |
| `provider_id` | 1 to 128 characters, starting with a letter or digit |
| `type` | must be a new type; the six built-in types are implemented in the core and cannot be declared by a pack |
| `version` | SemVer text |
| `host_compatibility` | optional inclusive host range `min`/`max`; dotted numeric versions, pre-release suffixes do not affect ordering, empty bounds are open-ended |
| `namespace` | `official/<plugin>`, `enterprise/<org>/<plugin>`, or another supported class |
| `source`, `source_root` | source identifiers, at most 128 characters, no `..` |
| `config_schema.dialect` | fixed to `cheesewaf-notifier-config/v1` |
| `config_schema.fields` | at most 24 fields; each has `name`, `kind`, `required`, and optional `max_length` (at most 2048) |
| `secret_fields` | at most 16 reference names, each ending in `_ref`; references only, never credential values |
| `endpoint_templates` | at most 4 templates; each has `name`, `url_template`, `method`, `egress_owner`, `variables` |
| `capabilities` | 1 to 2 items from `alert_delivery` and `test_delivery` |
| `publication` | fixed to `status=loadable`, `installable=false`, `crp_binding=descriptor-only` |

`endpoint_templates` rules:

- `url_template` starts with `https://` and is at most 512 characters.
- `method` is fixed to `POST`; `egress_owner` is fixed to `cheesewaf-core`.
- Template variables use `{name}` and must already be declared in
  `config_schema.fields` or `secret_fields`.
- The rendered URL must still point at the same host as the template, so a
  variable value cannot rewrite the destination.
- Templates never contain tokens, keys, or other credential values, and never
  contain a run of 32 or more letters or digits, so high-entropy values cannot
  be embedded directly in a URL.
- `secret_fields` stays a reference name only; the core injects credentials as
  request headers and never into the URL.

## Built-in types and pack types

| Built-in type | Purpose |
|---|---|
| `webhook` | generic JSON webhook |
| `dingtalk` | DingTalk group robot |
| `feishu` | Feishu custom bot |
| `wecom` | WeCom group robot |
| `telegram` | Telegram Bot API |
| `email` | core mail channel |

These six are compiled into the core. A pack can neither declare nor replace
them. To reach a new destination, a pack declares a new `type`; the core
resolves it from the index and configuration can use that type.

## Example

`examples/extensions/notifier-provider.json` is a `teams_webhook` contract
example. It fixes the notification URL template and the `webhook_ref` reference
name and declares a `host_compatibility` range, but contains no credential value
and no executable content.

The example exists only to check fields and boundaries. It is not installable
and is never parsed by CRP.

## Automated checks

`scripts/validate_notifier_contracts.py` in the publication repository checks:

- the schema and example parse strictly with no duplicate keys;
- the example validates and `publication` stays loadable, non-installable, and
  descriptor-only;
- `type` is not one of the six built-in types;
- `host_compatibility` bounds are dotted numeric versions;
- templates use HTTPS and core-owned egress;
- `secret_fields` comply and templates carry no high-entropy value;
- the file contains no executable or self-declared egress field.

These checks prove field and boundary consistency only. They do not prove
delivery, credential storage, retries, or audit are implemented.

## Current limits and next steps

- A provider pack has no CRP binding and cannot enter install, upgrade, or
  rollback flows.
- There are no catalog or OTA entries; the release indexes remain empty.
- Secret-reference resolution, delivery audit events, systematic retry and SSRF
  tests, and an administrator UI are still to be completed.
- Letting a plugin participate in notification requires a new capability,
  permission, and audit model. v1/v1.1 do not support it, and it must not be
  described as available before that design exists.

## Related pages

- [CRP Development Handbook](crp-development.en.md)
- [Store and OTA Contract](store-ota.en.md)
- [DuckDB Extension Contract](duckdb-extension.en.md)
