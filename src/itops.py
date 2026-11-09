"""Read-only local simulator for the Secure AI Agent for IT Operations project.

No network requests, production connections, credentials, or changes to accounts.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_json(name: str) -> list[dict]:
    with (ROOT / "data" / name).open(encoding="utf-8") as file:
        return json.load(file)


def list_tickets() -> list[dict]:
    return _read_json("tickets.json")


def get_ticket(ticket_id: str) -> dict | None:
    return next((item for item in list_tickets() if item["id"] == ticket_id), None)


def search_knowledge(query: str) -> list[dict]:
    query = query.casefold().strip()
    if not query:
        return []
    return [article for article in _read_json("knowledge.json")
            if query in (article["title"] + " " + " ".join(article["tags"]) + " " + " ".join(article["steps"])).casefold()]


def triage_ticket(ticket_id: str) -> dict | None:
    """Temporary rule-based baseline. An LLM-driven workflow will replace this later."""
    ticket = get_ticket(ticket_id)
    if ticket is None:
        return None
    text = (ticket["title"] + " " + ticket["description"]).casefold()
    if any(word in text for word in ("suspicious", "unexpected sign-in", "phishing", "malware")):
        category, priority = "Security", "High"
    elif "vpn" in text or "network" in text:
        category, priority = "Network", "Medium"
    elif "password" in text or "locked out" in text:
        category, priority = "Identity and Access", "Medium"
    elif "laptop" in text or "device" in text:
        category, priority = "Endpoint Support", "Low"
    else:
        category, priority = "General IT", "Low"
    return {
        "ticket_id": ticket_id,
        "category": category,
        "priority": priority,
        "basis": "Rule-based example classification. A human must verify before action.",
        "requires_human_review": True,
        "changes_made": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only IT operations simulator")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List fictional tickets")
    for command in ("show", "triage"):
        sub = commands.add_parser(command)
        sub.add_argument("ticket_id")
    kb = commands.add_parser("kb", help="Search fictional help articles")
    kb.add_argument("query")
    args = parser.parse_args()
    if args.command == "list":
        result = list_tickets()
    elif args.command == "show":
        result = get_ticket(args.ticket_id)
    elif args.command == "triage":
        result = triage_ticket(args.ticket_id)
    else:
        result = search_knowledge(args.query)
    if result is None:
        parser.error("Unknown ticket ID")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
