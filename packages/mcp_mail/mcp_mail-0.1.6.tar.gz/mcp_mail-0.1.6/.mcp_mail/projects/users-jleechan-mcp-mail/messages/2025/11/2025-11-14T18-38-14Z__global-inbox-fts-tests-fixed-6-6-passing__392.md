---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T18:38:14.893840+00:00",
  "from": "c3",
  "id": 392,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Global inbox FTS tests FIXED (6/6 passing)",
  "thread_id": null,
  "to": [
    "m"
  ]
}
---

## Summary

Fixed all 6 global inbox FTS test failures! The root cause was a SQLAlchemy 2.x compatibility issue with the FTS5 join syntax.

## Root Cause Analysis

After systematic investigation:

1. **IntegrityError (Fixed first)**: Global inbox was being added twice as a recipient:
   - Once in the `to` list (explicitly)
   - Once auto-added as `cc` (by auto-contact logic)
   - **Fix**: Updated `should_cc_global_inbox` check at app.py:2630-2636 to verify global inbox isn't already in `to_names` or `bcc_names`

2. **FTS5 query failing (Main issue)**: SQLAlchemy 2.x doesn't support `text()` in `.join()`:
   - Error: "Expected mapped entity or selectable/table as join target"
   - Old code: `.join(text("fts_messages ON messages.id = fts_messages.rowid"))`
   - **Fix**: Changed to subquery approach at app.py:1974:
     ```python
     text("messages.id IN (SELECT rowid FROM fts_messages WHERE fts_messages MATCH :agent_name)")
     ```

## Changes Made

### src/mcp_agent_mail/app.py

1. **Lines 2630-2636** - Fixed IntegrityError:
   ```python
   should_cc_global_inbox = (
       global_inbox_agent is not None
       and sender.name != global_inbox_name
       and global_inbox_name not in to_names  # NEW
       and global_inbox_name not in cc_names
       and global_inbox_name not in bcc_names  # NEW
   )
   ```

2. **Lines 1966-1977** - Fixed FTS5 query:
   ```python
   stmt = (
       select(Message, MessageRecipient.kind, sender_alias.name)
       .join(MessageRecipient, MessageRecipient.message_id == Message.id)
       .join(sender_alias, Message.sender_id == sender_alias.id)
       .where(
           MessageRecipient.agent_id == global_inbox_agent.id,
           # Use subquery approach for SQLAlchemy 2.x compatibility
           text("messages.id IN (SELECT rowid FROM fts_messages WHERE fts_messages MATCH :agent_name)"),
       )
       .order_by(desc(Message.created_ts))
   )
   ```

3. **Lines 1936-1939** - Added debug logging (can be removed if needed):
   ```python
   except Exception as e:
       logger.warning(f"Global inbox scan failed for agent {agent.name}: {e}", exc_info=True)
       pass
   ```

## Test Results

All 6 tests in `tests/test_global_inbox_scanning.py` now pass:
- ✅ test_inbox_includes_direct_messages_to_agent_from_global_inbox
- ✅ test_inbox_includes_messages_mentioning_agent_from_global_inbox
- ✅ test_inbox_includes_cc_messages_from_global_inbox
- ✅ test_inbox_deduplicates_messages_from_global_inbox
- ✅ test_inbox_mention_detection_case_insensitive
- ✅ test_inbox_global_scan_respects_limit

## Debug Files Created

Created `tests/test_fts_debug.py` to verify FTS5 table population and query execution. Can be kept for future debugging or removed.

## Recommendations

1. **Remove debug logging**: The warning log at app.py:1938 can be removed or made DEBUG level if you want cleaner production logs
2. **Clean up debug test**: Delete `tests/test_fts_debug.py` if not needed

All requested fixes are complete and tested!
