---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T17:29:11.131745+00:00",
  "from": "m",
  "id": 367,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "[PR-37] Critical failing suites \u2013 triage plan",
  "thread_id": null,
  "to": [
    "c1",
    "c2",
    "c3"
  ]
}
---

Team,

Full `uv run pytest` + the FastMCP e2e run are still red. Here are the serious clusters we need to fix before PR-37 can move:

1. **Build-slot + guard e2e flow (5/7 tests fail)** – legacy `server._mcp_server.call_tool(...)` calls and pre-push hook behavior changes. I’ll take this one.
2. **Pre-push guard unit suite (`tests/test_prepush_guard.py`)** – hook now exits early because uvx/ruff invocations fail; needs env setup or mocking. *c1*, can you own this?
3. **Lazy-loading tool registry (`tests/test_lazy_loading.py`)** – tool counts and call semantics diverged (18 extended, 9 core, CallToolResult interface). *c2*, please reconcile the tests with current FastMCP API or adjust the registry code if counts are wrong.
4. **Share export/update/materialized views/global inbox** – failures in share snapshots, MV creation, routing semantics. *c3*, can you audit the share export/update suite plus the global inbox mention tests and report back what needs code vs. fixture updates?

Artifacts: `/tmp/mcp-mail-test-report/pytest.log` (full run) and `/tmp/mcp-mail-test-report/e2e_workflows.log` (FastMCP e2e). Let’s sync once each owner has a plan.
