# Notifier Provider Pack Contract (planned)

This page defines the boundary for a notifier provider pack. The short version:
it is a contract only. It describes how the CheeseWAF core notifier delivers an
alert to a destination. It is not installable, carries no executable, and gives
a plugin no network egress. Current CRP v1 and the planned v1.1 sidecar do not
support notification egress.

## Compared with a sidecar

| Dimension | v1/v1.1 sidecar descriptor | notifier provider pack |
|---|---|---|
| Executable | asynchronous sidecar running code | no executable, image, WASM, or in-process module |
| Capabilities | `observe`, `candidate_snapshot`, `hint`, `health` | `alert_delivery`, `test_delivery`, contract labels only |
| Network | `egress` is fixed to `deny`; online access needs a short lease (not open yet) | no network stack; the core notifier resolves the target |
| Credentials | the plugin holds none | `secret_fields` holds reference names only; values stay in the core |
| Installation | handled by CWEDP/CRP (not live yet) | `installable=false`; cannot enter CRP |
| Format | CRP manifest plus sidecar descriptor | standalone JSON contract `crp.cheesewaf.io/notifier/v1` |

v1.1 is still a planned extension of sidecar capabilities and has no `notify`
permission. A provider pack never means "the plugin can send notifications".
Under the current contract, only the CheeseWAF core can deliver notifications.

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

| Field | Rule |
|---|---|
| `api_version` | fixed to `crp.cheesewaf.io/notifier/v1` |
| `provider_id` | 1 to 128 characters, starting with a letter or digit |
| `type` | one of the six types below |
| `version` | SemVer text |
| `namespace` | `official/<plugin>`, `enterprise/<org>/<plugin>`, or another supported class |
| `source`, `source_root` | source identifiers, at most 128 characters, no `..` |
| `config_schema.dialect` | fixed to `cheesewaf-notifier-config/v1` |
| `config_schema.fields` | at most 24 fields; each has `name`, `kind`, `required`, and optional `max_length` (at most 2048) |
| `secret_fields` | at most 16 reference names, each ending in `_ref`; references only, never credential values |
| `endpoint_templates` | at most 4 templates; each has `name`, `url_template`, `method`, `egress_owner`, `variables` |
| `capabilities` | 1 to 2 items from `alert_delivery` and `test_delivery` |
| `publication` | fixed to `status=planned`, `installable=false`, `crp_binding=descriptor-only` |

`endpoint_templates` rules:

- `url_template` starts with `https://` and is at most 512 characters.
- `method` is fixed to `POST`; `egress_owner` is fixed to `cheesewaf-core`.
- Template variables use `{name}` and must already be declared in
  `config_schema.fields` or `secret_fields`.
- Templates never contain tokens, keys, or other credential values, and never
  contain a run of 32 or more letters or digits, so high-entropy values cannot
  be embedded directly in a URL.
- An `email` provider may declare an empty `endpoint_templates` array because the
  core mail channel handles delivery; every other type must declare a `notify`
  template.

## Allowed types

| Type | Purpose |
|---|---|
| `webhook` | generic JSON webhook |
| `dingtalk` | DingTalk group robot |
| `feishu` | Feishu custom bot |
| `wecom` | WeCom group robot |
| `telegram` | Telegram Bot API |
| `email` | core mail channel |

A type is a contract category, not proof that a provider pack can be loaded.
The publication repository has no runtime loader for provider packs. The core
owns the delivery adapters, and their availability depends on core stage
acceptance.

## Example

`examples/extensions/notifier-provider.json` is the Feishu contract example. It
fixes the bot URL template and the `webhook_ref` field name, but contains no
credential value and no executable content.

The example exists only to check fields and boundaries. It is not installable,
is never parsed by CRP, and does not mean the pack can be loaded or has been
published.

## Automated checks

`scripts/validate_notifier_contracts.py` in the publication repository checks:

- the schema, policy, and example parse strictly with no duplicate keys;
- the example validates and `publication` stays planned and non-installable;
- type, capability, field names, and template variables stay in range;
- templates use HTTPS and core-owned egress;
- the policy grants no runtime capability, network egress, or executable.

These checks prove field and boundary consistency only. They do not prove
delivery, credential storage, retries, or audit are implemented.

## Current limits and next steps

- A provider pack has no CRP binding and cannot enter install, upgrade, or
  rollback flows.
- There are no catalog or OTA entries; the release indexes remain empty.
- The schema is registered under the public
  `store.cheesesec.com/schema/extensions/v1/` path; actual deployment is a
  separate store release decision.
- Making a provider pack effective still needs a core loader, secret-reference
  resolution, template expansion, delivery audit events, retry and SSRF tests,
  and an administrator UI.
- Letting a plugin participate in notification requires a new capability,
  permission, and audit model. v1/v1.1 do not support it, and it must not be
  described as available before that design exists.

## Related pages

- [CRP Development Handbook](crp-development.en.md)
- [Store and OTA Contract](store-ota.en.md)
- [DuckDB Extension Contract](duckdb-extension.en.md)
