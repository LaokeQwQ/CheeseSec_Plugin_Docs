#!/usr/bin/env python3
"""Validate the notifier provider pack contract and its example.

This enforces the boundary the core loader relies on: descriptor-only packs,
no executable content, no self-declared egress, no shadowing of built-in types,
and a host-compatibility range expressed as dotted numeric versions.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "extensions-v1" / "notifier-provider.schema.json"
EXAMPLE = ROOT / "examples" / "extensions" / "notifier-provider.json"

BUILTIN_TYPES = {"webhook", "dingtalk", "feishu", "wecom", "telegram", "email"}
EXECUTABLE_KEYS = {
    "executable",
    "executables",
    "entrypoint",
    "entrypoints",
    "artifact",
    "artifacts",
    "binary",
    "binaries",
    "script",
    "scripts",
    "command",
    "commands",
    "process",
    "install",
    "installer",
    "activation",
    "activate",
    "payload",
    "wasm",
}
EGRESS_KEYS = {
    "egress",
    "egress_targets",
    "egress_hosts",
    "egress_policy",
    "allowed_egress",
    "allow_egress",
    "outbound_hosts",
}
VERSION_BOUND = re.compile(r"^[0-9]+(\.[0-9]+){0,2}$")
HIGH_ENTROPY = re.compile(r"[A-Za-z0-9]{32,}")
SECRET_REF = re.compile(r"^[a-z][a-z0-9_]*_ref$")


def fail(message: str) -> None:
    raise SystemExit(f"notifier contract: {message}")


def load_strict(path: Path) -> dict:
    """Parse JSON rejecting duplicate keys, which json.load silently keeps."""
    duplicates: list[str] = []

    def hook(pairs):
        seen: set[str] = set()
        for key, _ in pairs:
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        return dict(pairs)

    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)
    if duplicates:
        fail(f"{path.relative_to(ROOT)} has duplicate keys: {sorted(set(duplicates))}")
    return data


def walk(value, trail: str = "") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if lowered in EXECUTABLE_KEYS:
                fail(f"field {trail}{key!r} would carry executable content")
            if lowered in EGRESS_KEYS:
                fail(f"field {trail}{key!r} would declare egress")
            walk(child, f"{trail}{key}.")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, f"{trail}[{index}].")


def validate_pack(pack: dict) -> None:
    if pack.get("api_version") != "crp.cheesewaf.io/notifier/v1":
        fail("api_version must be crp.cheesewaf.io/notifier/v1")

    provider_type = pack.get("type", "")
    if provider_type in BUILTIN_TYPES:
        fail(f"type {provider_type!r} is a built-in core type and cannot be declared by a pack")
    if not re.fullmatch(r"^[a-z][a-z0-9_]{1,63}$", provider_type):
        fail(f"type {provider_type!r} is not a lowercase identifier")

    compatibility = pack.get("host_compatibility", {})
    for bound in ("min", "max"):
        value = compatibility.get(bound)
        if value is not None and not VERSION_BOUND.fullmatch(value):
            fail(f"host_compatibility.{bound} {value!r} is not a dotted numeric version")

    publication = pack.get("publication", {})
    if publication.get("status") != "loadable":
        fail("publication.status must be loadable")
    if publication.get("installable") is not False:
        fail("publication.installable must be false")
    if publication.get("crp_binding") != "descriptor-only":
        fail("publication.crp_binding must be descriptor-only")

    declared = {field["name"] for field in pack.get("config_schema", {}).get("fields", [])}
    declared |= set(pack.get("secret_fields", []))
    for template in pack.get("endpoint_templates", []):
        if not template.get("url_template", "").startswith("https://"):
            fail(f"template {template.get('name')!r} must use https")
        if template.get("egress_owner") != "cheesewaf-core":
            fail(f"template {template.get('name')!r} must be owned by cheesewaf-core")
        if HIGH_ENTROPY.search(template.get("url_template", "")):
            fail(f"template {template.get('name')!r} embeds a high-entropy value")
        for variable in template.get("variables", []):
            if variable not in declared:
                fail(f"template {template.get('name')!r} uses undeclared variable {variable!r}")

    for name in pack.get("secret_fields", []):
        if not SECRET_REF.fullmatch(name):
            fail(f"secret field {name!r} must be a *_ref reference name")


def main() -> int:
    schema = load_strict(SCHEMA)
    example = load_strict(EXAMPLE)

    if schema.get("properties", {}).get("type", {}).get("not", {}).get("enum") != sorted(
        BUILTIN_TYPES, key=lambda value: ["webhook", "dingtalk", "feishu", "wecom", "telegram", "email"].index(value)
    ):
        fail("schema type rule must exclude the six built-in types")

    walk(schema)
    walk(example)
    validate_pack(example)

    try:
        import jsonschema
    except ImportError:
        fail("jsonschema is required (requirements-ci-linux.txt)")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(example)

    print("notifier contract OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
