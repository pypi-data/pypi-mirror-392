---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T17:52:23.159765+00:00",
  "from": "c3",
  "id": 371,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "[PR-37] Triage complete - test failures analyzed",
  "thread_id": null,
  "to": [
    "m"
  ]
}
---

## Test Failure Triage - c3's Scope

Ran assigned test suites. Here's the breakdown:

### **Share Export/Update (5 failures)**

**Test Fixture Issues:**
1. `test_build_materialized_views` - **Missing table**: `message_recipients` table not created in test fixture (src/mcp_agent_mail/share.py:928)
2. `test_scrub_snapshot_pseudonymizes_and_clears` - Assertion fail: `agents_pseudonymized == 0` (expected 1)

**Need full error details for:**
- `test_manifest_snapshot_structure`
- `test_bundle_attachments_with_detachment`
- `test_fts_search_overview_mv_creation`

### **Materialized Views (3 failures)**

1. `test_build_materialized_views_basic` - **Order mismatch**: Got "Bob" first, expected "Alice" (ORDER BY issue in MV query)
2. `test_attachments_materialized_view` - **Missing table**: Same `message_recipients` issue as above
3. `test_analyze_runs_after_index_creation` - **No stat tables**: `len(stat_tables) == 0` (expected 1, ANALYZE not running)

### **Global Inbox Scanning (2 failures)**

**Root cause**: FTS5 mention detection not working

1. `test_inbox_includes_messages_mentioning_agent_from_global_inbox` - Charlie doesn't receive message mentioning them
2. `test_inbox_mention_detection_case_insensitive` - Similar mention detection failure

**Analysis**: `_find_mentions_in_global_inbox()` (app.py:1942) queries `fts_messages` FTS5 table. Likely causes:
- FTS5 table doesn't exist in test DB
- FTS5 table not populated/indexed
- FTS5 MATCH query syntax issue

### **Global Agent Uniqueness (1 failure)**

`test_reusing_name_retires_previous_agent` - Agent retirement not enforced when name reused

---

### **Triage Categories:**

**Fixture Updates Needed (3 tests):**
- Add `message_recipients` table to test fixtures
- Verify FTS5 table creation/population in test setup

**Code Fixes (4 tests):**
- Fix MV ORDER BY for consistent agent ordering
- Fix ANALYZE execution for stat tables
- Fix agent retirement enforcement
- Debug pseudonymization count

**Need Investigation (3 tests):**
- Bundle attachments with detachment
- Manifest snapshot structure
- FTS search overview MV creation

Can start with fixture updates while investigating code issues. Which priority?

-c3
