import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "src" / "itops.py"
spec = importlib.util.spec_from_file_location("itops", PATH)
itops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(itops)


class ITToolsTests(unittest.TestCase):
    def test_four_sample_tickets(self):
        self.assertEqual(len(itops.list_tickets()), 4)

    def test_suspicious_login_is_high_priority(self):
        result = itops.triage_ticket("INC-1001")
        self.assertEqual(result["category"], "Security")
        self.assertEqual(result["priority"], "High")
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["changes_made"])

    def test_vpn_knowledge(self):
        self.assertEqual(itops.search_knowledge("vpn")[0]["id"], "KB-002")

    def test_unknown_ticket_is_not_found(self):
        self.assertIsNone(itops.triage_ticket("INC-9999"))

    def test_empty_query_returns_nothing(self):
        self.assertEqual(itops.search_knowledge("  "), [])


if __name__ == "__main__":
    unittest.main()
