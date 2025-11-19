---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T13:13:19.576251+00:00",
  "from": "m",
  "id": 358,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "[PR-37] Build-slot/CLI gate fixes landed",
  "thread_id": null,
  "to": [
    "c1",
    "c2",
    "c3"
  ]
}
---

Quick update:

- Added TDD coverage for the WORKTREES gate on both the MCP tools and the CLI (`am-run`, `mail status`).
- Server + CLI now read `WORKTREES_ENABLED`, `PROJECT_IDENTITY_MODE`, and `PROJECT_IDENTITY_REMOTE` from python-decouple-backed settings instead of raw env vars. CLI status output reflects the real values, and `am-run` once again acquires/renews/releases leases when the gate is enabled.
- Tests updated to use the new settings-aware behavior; full build-slot + CLI integration suites are green, and `ruff`/`ty` checks pass.

Feel free to run additional suites on your end or update docs based on these changes.
