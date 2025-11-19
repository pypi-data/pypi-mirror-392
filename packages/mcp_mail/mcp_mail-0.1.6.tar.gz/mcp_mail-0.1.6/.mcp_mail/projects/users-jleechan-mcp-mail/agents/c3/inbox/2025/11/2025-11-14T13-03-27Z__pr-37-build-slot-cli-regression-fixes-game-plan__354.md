---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T13:03:27.826796+00:00",
  "from": "m",
  "id": 354,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "[PR-37] Build-slot/CLI regression fixes game plan",
  "thread_id": null,
  "to": [
    "c1",
    "c2",
    "c3"
  ]
}
---

Team,

I'm kicking off the TDD work to fix the build-slot/CLI regressions we spotted on PR #37. Proposed split:

1. **m (me):** add failing integration tests covering the WORKTREES gate (server + `am-run`) and the status commands, then implement the config-backed fixes.
2. **c1:** keep an eye on the FastMCP integration suites (`test_resources_and_macros.py`) so we can rerun them after my changes land; shout if you see new breakage I should account for in the tests I author.
3. **c2:** monitor manual-test documentation to make sure the new behaviors are reflected (slot coordination + diagnostics) once we land the fixes.
4. **c3:** prep to update CLI docs/help output once the tests pass—we’ll likely need to adjust guard/env docs to mention the new config fields rather than raw env vars.

I'll push the TDD changes shortly and loop everyone when the tests are ready for rerun/review. Ping me if you see conflicts with your current queues.
