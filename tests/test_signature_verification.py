from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.signature_verifier import verify_signature_set


ROOT = Path(__file__).resolve().parents[1]


class HandbookSignatureTests(unittest.TestCase):
    def test_signed_example_is_verifiable_offline(self) -> None:
        result = verify_signature_set(
            (ROOT / "examples/crp-v1/manifest.json").read_bytes(),
            (ROOT / "examples/crp-v1/signatures/manifest.json").read_bytes(),
            json.loads((ROOT / "policy/trust-roots.json").read_text(encoding="utf-8")),
            json.loads((ROOT / "policy/source-registry.json").read_text(encoding="utf-8")),
            json.loads((ROOT / "policy/revocations.json").read_text(encoding="utf-8")),
            now=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(result["trust_level"], "official")
        self.assertEqual(len(result["valid_key_ids"]), 2)


if __name__ == "__main__":
    unittest.main()
