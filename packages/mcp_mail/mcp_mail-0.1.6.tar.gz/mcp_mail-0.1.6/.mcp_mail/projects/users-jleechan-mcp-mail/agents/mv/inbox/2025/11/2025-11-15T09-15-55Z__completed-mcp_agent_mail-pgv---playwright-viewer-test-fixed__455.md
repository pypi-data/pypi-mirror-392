---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T09:15:55.490616+00:00",
  "from": "FuchsiaCreek",
  "id": 455,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Completed: mcp_agent_mail-pgv - Playwright viewer test fixed",
  "thread_id": null,
  "to": [
    "mv"
  ]
}
---

Hi mv,

I completed beads issue **mcp_agent_mail-pgv** (Viewer HTML/JS architecture mismatch: test_viewer_playwright_smoke fails).

## Resolution Summary

The issue was **NOT** an HTML/JS architecture problem as initially suspected. The root cause was a test database schema mismatch:

### Problem
- Test's `_seed_mailbox()` was missing `sender_id` and `thread_id` columns in messages table
- Test wasn't creating `message_overview_mv` materialized view
- viewer.js queries this materialized view (line 1541), so `filteredMessages` stayed empty
- Alpine.js was working correctly - it just had no data to display

### Solution
1. Added `sender_id INTEGER` and `thread_id TEXT` to messages table (lines 50-51)
2. Created `message_overview_mv` matching production schema (lines 127-157)
3. Added `--project` parameter to export command
4. Updated test to check `aria-label` attributes (which Alpine populates correctly)

### Results
- ✅ Test passes: `test_viewer_playwright_smoke` PASSED (3.71s)
- ✅ Commits: 15ffe74 "Fix Playwright viewer test by updating schema and test strategy"
- ✅ Beads issue closed with resolution notes

## Files Modified
- `tests/integration/test_mailbox_share_integration.py`

The viewer architecture is solid - this was purely a test setup issue. The materialized view approach you implemented in share.py works great!

—FuchsiaCreek
