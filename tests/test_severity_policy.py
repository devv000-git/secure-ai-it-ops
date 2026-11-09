"""Evaluation tests for the fictional IT incident severity policy."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "itops", ROOT / "src" / "itops.py"
)
itops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(itops)


class SeverityPolicyTests(unittest.TestCase):

    def check_ticket(self, ticket_id, category, priority):
        result = itops.triage_ticket(ticket_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], category)
        self.assertEqual(result["priority"], priority)
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["changes_made"])

    def test_suspicious_signin(self):
        self.check_ticket("INC-1001", "Security", "High")

    def test_vpn_failure(self):
        self.check_ticket("INC-1002", "Network", "Medium")

    def test_slow_laptop(self):
        self.check_ticket("INC-1003", "Endpoint Support", "Low")

    def test_password_reset(self):
        self.check_ticket(
            "INC-1004", "Identity and Access", "Medium"
        )

    def test_unknown_ticket(self):
        self.assertIsNone(itops.triage_ticket("INC-9999"))


if __name__ == "__main__":
    unittest.main()
