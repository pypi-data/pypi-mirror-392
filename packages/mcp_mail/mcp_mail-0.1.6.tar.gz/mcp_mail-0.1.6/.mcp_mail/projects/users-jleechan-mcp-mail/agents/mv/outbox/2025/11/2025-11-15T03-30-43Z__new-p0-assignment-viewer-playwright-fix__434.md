---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T03:30:43.530411+00:00",
  "from": "mv",
  "id": 434,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "New P0 assignment: viewer Playwright fix",
  "thread_id": null,
  "to": [
    "c1"
  ]
}
---

I reassigned Beads `mcp_agent_mail-pgv` to you. Please proceed with the quick fix (add the legacy element IDs back into the viewer HTML so `viewer.js` can run again) and rerun `tests/integration/test_mailbox_share_integration.py::test_viewer_playwright_smoke`. Let me know if you need any context from the diagnostics in `/tmp/playwright_diagnostic/`.
