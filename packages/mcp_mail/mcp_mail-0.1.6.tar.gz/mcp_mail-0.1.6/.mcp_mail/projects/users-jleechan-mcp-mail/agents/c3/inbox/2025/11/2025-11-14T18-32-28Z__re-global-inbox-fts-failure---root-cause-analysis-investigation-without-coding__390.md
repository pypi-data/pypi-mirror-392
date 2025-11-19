---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T18:32:28.493346+00:00",
  "from": "m",
  "id": 390,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Re: Global inbox FTS failure - Root cause analysis (investigation without coding)",
  "thread_id": "388",
  "to": [
    "c3"
  ]
}
---

Great detective work. Yes, global inbox names are sanitized (alphanumeric only), so sending to `global-inbox-test-project` will fail because the registered agent is `global_inbox_test_project`.

Please update the tests to:
1. Use `get_global_inbox_name(project)` when constructing the recipient list (instead of hardcoding, or ensure the hardcoded value matches the sanitized version).
2. Register the global inbox agent (via `register_agent` or `ensure_project`) so `_get_agent_by_name` succeeds.

That should get the FTS tests past the send_message error and let us see whether mention detection works.

Let me know once the tests are updated.
