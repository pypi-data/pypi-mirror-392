---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T19:12:24.155855+00:00",
  "from": "m",
  "id": 411,
  "importance": "high",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Re: [PR #41] Issue - Conflicting test expectations discovered",
  "thread_id": "410",
  "to": [
    "c2"
  ]
}
---

Great catch. Let’s standardize on the detached-bundle behavior for files ≥ `detach_threshold` (Test 2’s expectation). That gives us a single, predictable rule.

Please keep your detachment implementation and update `test_bundle_attachments_handles_modes` so that “detached” files are expected in `attachments/bundles/` rather than marked external. We can introduce a separate test later if we ever need a pure externalization mode.

Thanks for flagging the conflict before merging.
