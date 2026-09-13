#!/usr/bin/env python3
"""Validate the handbook mirror of the store/OTA commercial contracts."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parent / "CheeseSec_Plugin"
SCHEMA_DIR = ROOT / "schema" / "store-v1"


def strict_load(path: Path) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{path}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def _validate(instance: Any, schema: dict[str, Any], label: str) -> None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        path = ".".join(str(part) for part in errors[0].path)
        raise ValueError(f"{label}: {path + ': ' if path else ''}{errors[0].message}")


def validate() -> None:
    names = ["trust-levels", "endpoint-policy", "cwedp", "release", "catalog", "ota", "sidecar-descriptor", "offline-import"]
    schemas = {name: strict_load(SCHEMA_DIR / f"{name}.schema.json") for name in names}
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        if PLUGIN_ROOT.is_dir():
            canonical = PLUGIN_ROOT / "schema" / "store-v1" / f"{name}.schema.json"
            if canonical.read_bytes() != (SCHEMA_DIR / f"{name}.schema.json").read_bytes():
                raise ValueError(f"schema mirror differs from publication repository: {name}")
    contracts = {
        "trust": strict_load(ROOT / "policy" / "trust-levels.json"),
        "endpoints": strict_load(ROOT / "policy" / "endpoints.json"),
        "cwedp": strict_load(ROOT / "policy" / "cwedp.json"),
        "offline": strict_load(ROOT / "policy" / "offline-import.json"),
        "catalog": strict_load(ROOT / "catalog" / "index.json"),
        "ota": strict_load(ROOT / "ota" / "index.json"),
        "sidecar": strict_load(ROOT / "examples" / "store-v1" / "sidecar-descriptor.json"),
        "release": strict_load(ROOT / "examples" / "store-v1" / "release-record.json"),
    }
    _validate(contracts["trust"], schemas["trust-levels"], "trust-levels policy")
    _validate(contracts["endpoints"], schemas["endpoint-policy"], "endpoint policy")
    _validate(contracts["cwedp"], schemas["cwedp"], "CWEDP policy")
    _validate(contracts["offline"], schemas["offline-import"], "offline import policy")
    _validate(contracts["sidecar"], schemas["sidecar-descriptor"], "sidecar descriptor")
    _validate(contracts["release"], schemas["release"], "release example")
    catalog_schema = copy.deepcopy(schemas["catalog"])
    catalog_schema["properties"]["releases"]["items"] = schemas["release"]
    _validate(contracts["catalog"], catalog_schema, "catalog index")
    _validate(contracts["ota"], schemas["ota"], "OTA index")
    endpoints = {entry["id"]: entry for entry in contracts["endpoints"]["endpoints"]}
    expected_paths = {
        "store": [
            "/v1/catalog/index.json",
            "/v1/policy/endpoints.json",
            "/v1/policy/trust-roots.json",
            "/v1/policy/source-registry.json",
            "/v1/policy/revocations.json",
            "/v1/schema/store/{name}.schema.json",
            "/v1/schema/crp/{name}.schema.json",
        ],
        "ota": ["/v1/channels/{channel}/index.json"],
        "resources": ["/sha256/{sha256}/{filename}"],
    }
    if {key: endpoints[key]["paths"] for key in expected_paths} != expected_paths:
        raise ValueError("endpoint paths do not match the fixed edge route contract")
    if any(entry["origin_role"] != "edge-public-r2" for entry in endpoints.values()):
        raise ValueError("public publication endpoints must use the edge-public-r2 origin role")
    if endpoints["store"]["cache_class"] != "short-revalidate" or endpoints["ota"]["cache_class"] != "short-revalidate":
        raise ValueError("store and OTA indexes must use short revalidation")
    if endpoints["resources"]["cache_class"] != "immutable":
        raise ValueError("resource endpoint must use immutable caching")
    if contracts["cwedp"]["pull_only"] is not True or contracts["cwedp"]["ansible_push"] is not False:
        raise ValueError("CWEDP must be pull-only and Ansible push must be disabled")
    if contracts["sidecar"]["runtime"] != "sidecar" or contracts["sidecar"]["metadata"]["request_path"] != "asynchronous":
        raise ValueError("sidecar descriptor must be 34A asynchronous sidecar")
    if contracts["catalog"]["releases"] or contracts["ota"]["releases"]:
        raise ValueError("handbook mirror starts fail-closed with empty live indexes")
    print("handbook commercial contract mirror passed")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"handbook commercial contract validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
