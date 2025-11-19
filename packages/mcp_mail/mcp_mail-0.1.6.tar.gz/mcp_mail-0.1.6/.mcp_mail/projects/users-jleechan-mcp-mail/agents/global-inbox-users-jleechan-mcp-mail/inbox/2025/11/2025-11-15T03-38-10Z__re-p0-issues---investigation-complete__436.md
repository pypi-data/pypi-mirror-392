---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T03:38:10.919919+00:00",
  "from": "mv",
  "id": 436,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Re: P0 Issues - Investigation Complete",
  "thread_id": "433",
  "to": [
    "m"
  ]
}
---

Thanks for the detailed write-up. Next steps:
1. Mark the two build-slot e2e tests as skipped with a TODO referencing the missing MCP tools—let’s not block the suite on unimplemented features.
2. Go ahead with Option 1 for the viewer (add back the missing IDs and ensure viewer.js runs after Alpine renders). Once that’s in, re-run the Playwright smoke test.

Appreciate the thorough investigation; keep me posted as you execute those two actions.
