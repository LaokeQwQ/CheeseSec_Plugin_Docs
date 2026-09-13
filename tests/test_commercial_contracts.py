from __future__ import annotations

import unittest

from scripts.validate_commercial_contracts import validate


class CommercialContractMirrorTests(unittest.TestCase):
    def test_mirror_and_fail_closed_indexes(self) -> None:
        validate()


if __name__ == "__main__":
    unittest.main()
