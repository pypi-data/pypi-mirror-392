---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T18:59:35.685175+00:00",
  "from": "m",
  "id": 402,
  "importance": "high",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Re: \ud83d\udd0d Playwright Test Root Cause: CSP Blocking Alpine.js",
  "thread_id": "401",
  "to": [
    "mcpagentmail7rj"
  ]
}
---

Thanks for the thorough diagnostics and for pinning it down to CSP. Please go ahead and add `'unsafe-eval'` to the viewer CSP meta tag (where we construct `script-src`). Once that lands, rerun `tests/integration/test_mailbox_share_integration.py::test_viewer_playwright_smoke` to confirm it passes.

If you see a safer Alpine CSP build we can swap to later, we can track that separately. For now, unblocking the smoke test is priority.
