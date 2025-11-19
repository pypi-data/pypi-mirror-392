---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T10:30:02.055825+00:00",
  "from": "c2",
  "id": 470,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "\u2705 externalized_count bug fixed - PR #41 updated (TDD complete)",
  "thread_id": null,
  "to": [
    "m"
  ]
}
---

Hi m,

**Bug fix complete** - externalized_count removed from bundle_attachments stats following TDD protocol from message #462.

## TDD Results

### 1. ❌ Test output BEFORE fix
```
AssertionError: externalized field should be removed entirely
assert 'externalized' not in {'bytes_copied': 20000, 'copied': 1, 'externalized': 0, 'inline': 1, ...}
```
**Evidence**: Variable initialized but never incremented, always returning 0 in stats.

### 2. 📝 Code changes made

**src/mcp_agent_mail/share.py**:
- Removed `externalized_count = 0` variable (lines 1267-1271)
- Removed `"externalized": externalized_count` from stats dict (line 1420)
- Stats API simplified to: `{"inline", "copied", "missing", "bytes_copied"}`

**tests/test_share_export.py**:
- Removed `"externalized": 0` assertion from test_bundle_attachments_handles_modes

**tests/integration/test_mailbox_share_integration.py**:
- Removed `assert stats["externalized"] == 0` from test_share_export_end_to_end

### 3. ✅ Test output AFTER fix
```
============================== 2 passed in 1.18s ===============================
```
**Evidence**: All share export/update tests passing with corrected expectations.

### 4. ✅ Full test suite results
```
======================== 48 passed, 1 failed in 35.83s =========================
```
**Status**: 
- ✅ 48/48 share export/update tests passing (excl. Playwright)
- ✅ test_bundle_attachments_handles_modes - PASS
- ✅ test_share_export_end_to_end - PASS  
- ⚠️ 1 Playwright timeout is pre-existing (mcp_agent_mail-pgv)

## PR Status

- **Commit**: `56955f8` - Remove externalized_count field from bundle_attachments stats
- **Branch**: fix/share-export-update-tests (PR #41)
- **Pushed**: https://github.com/jleechanorg/mcp_mail/pull/41
- **CI**: Running now

## Summary

Followed your recommendation for **Option 1: Remove entirely**. This was indeed the cleaner solution:
- Eliminates misleading field that was always 0
- Aligns with detached bundles feature semantics  
- Simplifies stats API surface

Thanks for catching this - just documenting it wasn't the right fix.

— c2
