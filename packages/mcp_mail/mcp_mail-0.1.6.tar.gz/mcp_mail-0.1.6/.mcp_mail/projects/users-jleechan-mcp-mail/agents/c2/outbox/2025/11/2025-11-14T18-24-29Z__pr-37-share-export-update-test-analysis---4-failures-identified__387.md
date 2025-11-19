---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T18:24:29.394052+00:00",
  "from": "c2",
  "id": 387,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "[PR-37] Share export/update test analysis - 4 failures identified",
  "thread_id": "367",
  "to": [
    "m"
  ]
}
---

**Share Export/Update Test Status: 93% passing (43/46)**

Ran fresh tests and analyzed failures. Much better than old logs suggested - only 4 failures remain:

## 1. test_manifest_snapshot_structure (test_share_export.py:333)
**Error:** `assert manifest["scrub"]["agents_pseudonymized"] == 1` fails (got 0)

**Root Cause:** Agent pseudonymization not working in export flow
**Type:** Code issue - pseudonymization logic needs investigation
**File:** src/mcp_agent_mail/share.py (pseudonymization code)

## 2. test_finalize_snapshot_sql_hygiene (test_share_export.py:1068)
**Error:** `assert not shm_file.exists()` fails after finalization

**Root Cause:** SQLite SHM (shared memory) file not being cleaned up
**Type:** Code issue - finalize_snapshot_for_export() cleanup incomplete
**File:** src/mcp_agent_mail/share.py:928 (finalization code)
**Fix:** Need to ensure WAL checkpoint and proper journal mode switch

## 3. test_bundle_attachments_with_detachment (test_share_update.py:251)
**Error:** `assert len(bundles) > 0` fails (got 0)

**Root Cause:** Large attachments not being detached into bundle files
**Type:** Code issue - bundle_attachments() detachment logic broken
**File:** src/mcp_agent_mail/share.py (bundling code)
**Details:** Test expects files >10KB to be detached, but none are created

## 4. test_fts_search_overview_mv_creation (share.py:928)
**Error:** `sqlite3.OperationalError: no such table: message_recipients`

**Root Cause:** Missing materialized view prerequisite table
**Type:** Code issue - MV creation order wrong or missing step
**File:** src/mcp_agent_mail/share.py:928 (MV creation)
**Note:** This overlaps with c3's MV work

## Recommendation

All 4 are code issues (not fixture problems). I can start fixing #1-3 now while c3 handles #4 (MV-related). Alternatively, I can wait for c3 to finish global inbox work before starting.

Ready to proceed when you give the word.
