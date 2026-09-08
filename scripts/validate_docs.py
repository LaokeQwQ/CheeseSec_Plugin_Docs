#!/usr/bin/env python3
"""Validate required bilingual handbook pages and local Markdown links."""
from __future__ import annotations

import sys

from validate_crp_v1 import validate_handbook


if __name__ == "__main__":
    try:
        validate_handbook()
    except (OSError, ValueError) as exc:
        print(f"documentation validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
