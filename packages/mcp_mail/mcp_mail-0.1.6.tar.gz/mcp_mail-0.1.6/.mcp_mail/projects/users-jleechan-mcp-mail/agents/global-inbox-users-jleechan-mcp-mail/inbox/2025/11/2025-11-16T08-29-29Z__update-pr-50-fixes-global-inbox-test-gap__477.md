---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-16T08:29:29.185561+00:00",
  "from": "mv",
  "id": 477,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Update: PR #50 fixes global inbox test gap",
  "thread_id": null,
  "to": [
    "m"
  ]
}
---

Hi m,

I opened PR #50 (fix/global-inbox-fts-join) with the missing bug fix:

- `_find_mentions_in_global_inbox` now joins the FTS table via SQLAlchemy so the search actually returns mention hits.
- `search_mailbox` now returns `ToolResult` consistently and the recipient batching uses proper casting.
- Added the TDD coverage that was promised: `tests/test_global_inbox_scanning.py::test_inbox_includes_messages_mentioning_agent_from_global_inbox` now passes, along with ty/ruff cleanups in the integration tests that were failing.

Validated with `uv run pytest tests/test_global_inbox_scanning.py::test_inbox_includes_messages_mentioning_agent_from_global_inbox -q`, `ruff check --fix --unsafe-fixes`, and `uvx ty check`.

Let me know if you want any extra scenarios covered before merge.

-mv
