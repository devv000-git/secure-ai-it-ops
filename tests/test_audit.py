"""Automated tests for IT Operations MCP audit logging."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from audit import record_audit_event
from mcp_server import audited_tool_call


class AuditLoggingTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env_patch = patch.dict(
            os.environ,
            {"ITOPS_AUDIT_DIR": self.temp_dir.name}
        )
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    def read_events(self):
        log_path = Path(self.temp_dir.name) / "tool_calls.jsonl"
        with log_path.open(encoding="utf-8") as file:
            return [json.loads(line) for line in file]

    def test_successful_operation_logged(self):
        result = audited_tool_call(
            "read_it_ticket",
            lambda: {"id": "INC-1001"},
            ticket_id="INC-1001",
        )

        self.assertEqual(result["id"], "INC-1001")

        events = self.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["status"], "success")
        self.assertEqual(events[0]["ticket_id"], "INC-1001")
        self.assertTrue(events[0]["read_only"])

    def test_missing_ticket_logged(self):
        audited_tool_call(
            "read_it_ticket",
            lambda: {"error": "Ticket not found"},
            ticket_id="INC-9999",
        )

        events = self.read_events()
        self.assertEqual(events[0]["status"], "not_found")
        self.assertEqual(
            events[0]["error_code"],
            "RESOURCE_NOT_FOUND",
        )

    def test_failed_operation_logged(self):
        def failing_operation():
            raise ValueError("Simulated operation failure")

        with self.assertRaises(ValueError):
            audited_tool_call(
                "read_it_ticket",
                failing_operation,
                ticket_id="INC-1001",
            )

        events = self.read_events()
        self.assertEqual(events[0]["status"], "error")
        self.assertEqual(
            events[0]["error_code"],
            "OPERATION_FAILED",
        )

    def test_sensitive_content_not_logged(self):
        secret_text = "CONFIDENTIAL_TEST_CONTENT"

        audited_tool_call(
            "search_it_knowledge",
            lambda: [{"description": secret_text}],
        )

        log_path = Path(self.temp_dir.name) / "tool_calls.jsonl"
        content = log_path.read_text(encoding="utf-8")

        self.assertNotIn(secret_text, content)
        self.assertNotIn("description", content)


if __name__ == "__main__":
    unittest.main()
