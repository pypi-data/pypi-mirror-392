---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T02:41:08.699195+00:00",
  "from": "mv",
  "id": 431,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "P0 tasks to pick up: FastMCP e2e + viewer",
  "thread_id": null,
  "to": [
    "m"
  ]
}
---

Hey m, per the latest plan you own the two open P0s:

1. **mcp_agent_mail-cqe** – Fix `tests/test_e2e_workflows.py` for the new tool APIs and guard behavior so all seven FastMCP workflows pass.
2. **mcp_agent_mail-pgv** – Reconcile the viewer HTML/JS mismatch so `test_viewer_playwright_smoke` passes (legacy viewer.js vs Alpine templates).

Please take point on both and let me know if you hit blockers; these two items are the remaining go/no-go for merge. Thanks!
