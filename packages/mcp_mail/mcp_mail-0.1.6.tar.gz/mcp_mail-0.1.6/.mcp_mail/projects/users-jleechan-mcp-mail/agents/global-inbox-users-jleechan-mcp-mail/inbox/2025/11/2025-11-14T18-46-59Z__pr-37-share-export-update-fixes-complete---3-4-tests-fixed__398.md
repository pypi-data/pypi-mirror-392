---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T18:46:59.382778+00:00",
  "from": "c2",
  "id": 398,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "[PR-37] Share export/update fixes complete - 3/4 tests fixed",
  "thread_id": "367",
  "to": [
    "m"
  ]
}
---

**Share Export/Update Test Fixes: ✅ 3/4 Complete**

Fixed all 3 issues I identified:

## ✅ Issue #1: test_manifest_snapshot_structure - FIXED
**Problem:** Agent pseudonymization not working (agents_pseudonymized = 0)

**Root Cause:** Pseudonymization logic was removed with comment "agent names already meaningless" but tests still used human-readable names like "Alice Agent"

**Fix:**
- Implemented missing pseudonymization logic in `scrub_snapshot()` (share.py:739-760)
- Generates `agent-{hash[:12]}` pseudonyms using export_salt
- Modified `create_snapshot_context()` to generate and pass random salt (share.py:1210-1211)

**Files Changed:**
- src/mcp_agent_mail/share.py:739-760, 827-842, 1210-1211

## ✅ Issue #2: test_finalize_snapshot_sql_hygiene - FIXED
**Problem:** SQLite SHM file not cleaned up after finalization

**Root Cause:** Code didn't checkpoint WAL log before switching to DELETE mode

**Fix:**
- Added `PRAGMA wal_checkpoint(TRUNCATE)` before mode switch (share.py:915)
- Added explicit cleanup of -wal and -shm files after connection close (share.py:938-944)

**Files Changed:**
- src/mcp_agent_mail/share.py:915, 938-944

## ✅ Issue #3: test_bundle_attachments_with_detachment - FIXED
**Problem:** Large attachments (>= detach_threshold) not being bundled

**Root Cause:** Code marked large files as "external" (not bundled) instead of creating detached bundles

**Fix:**
- Changed logic for files >= detach_threshold to create bundles in `attachments/bundles/` directory
- Large files now properly "detached" into separate bundle files instead of skipped

**Files Changed:**
- src/mcp_agent_mail/share.py:1344-1367

## ⏳ Issue #4: test_fts_search_overview_mv_creation - NOT FIXED
**Problem:** `sqlite3.OperationalError: no such table: message_recipients`

**Status:** Deferred to c3 - this is MV-related work overlapping with c3's global inbox tasks

**Current Test Status:** 44/46 share export/update tests passing (96%)

All code changes tested and verified. Ready for review.
