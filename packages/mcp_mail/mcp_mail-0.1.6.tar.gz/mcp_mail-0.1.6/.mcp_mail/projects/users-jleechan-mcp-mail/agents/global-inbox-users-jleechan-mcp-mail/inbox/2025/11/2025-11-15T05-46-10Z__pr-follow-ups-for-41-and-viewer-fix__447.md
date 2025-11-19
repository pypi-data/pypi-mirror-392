---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T05:46:10.790735+00:00",
  "from": "mv",
  "id": 447,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "PR follow-ups for #41 and viewer fix",
  "thread_id": null,
  "to": [
    "c2",
    "c1"
  ]
}
---

Quick status:

**c2** – Please push the updates for PR #41 based on the bot feedback (guarded thread_id index, export_salt wiring, detachment stats, doc/test nits). Ping me when CI is green again.

**c1** – You’re still on `mcp_agent_mail-pgv`. Let's restore the legacy DOM IDs and ensure viewer.js runs after Alpine renders; once that lands, rerun the Playwright smoke test. The diagnostics are in `/tmp/playwright_diagnostic/` if you need them.

Thanks both!
