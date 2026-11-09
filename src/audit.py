"""Structured audit logging for the IT Operations MCP server."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_AUDIT_DIR = "/opt/data/itops-audit"


def record_audit_event(
    tool: str,
    status: str,
    ticket_id: str | None = None,
    error_code: str | None = None,
) -> dict:
    """Append a minimal audit event to a JSONL file."""

    directory = Path(
        os.environ.get("ITOPS_AUDIT_DIR", DEFAULT_AUDIT_DIR)
    )
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "mcp_tool_call",
        "tool": tool,
        "ticket_id": ticket_id,
        "status": status,
        "read_only": True,
        "error_code": error_code,
    }

    output = directory / "tool_calls.jsonl"
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    flags |= getattr(os, "O_NOFOLLOW", 0)

    fd = os.open(output, flags, 0o600)

    with os.fdopen(fd, "a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")

    return event
