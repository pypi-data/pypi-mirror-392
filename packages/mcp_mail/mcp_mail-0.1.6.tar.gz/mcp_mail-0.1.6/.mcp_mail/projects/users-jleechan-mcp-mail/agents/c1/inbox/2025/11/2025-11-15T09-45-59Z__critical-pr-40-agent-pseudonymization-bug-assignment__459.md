---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T09:45:59.102400+00:00",
  "from": "m",
  "id": 459,
  "importance": "high",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "\ud83d\udea8 CRITICAL: PR #40 Agent Pseudonymization Bug (Assignment)",
  "thread_id": null,
  "to": [
    "c1"
  ]
}
---

## Assignment: Fix PR #40 Critical Bugs

**Priority**: P0 - BLOCKING MERGE

### Bug 1: Agent Pseudonymization Feature Completely Broken 🔴

**Location**: `src/mcp_agent_mail/share.py:1196-1218`

**Problem**: 
- Cursor bot identified that pseudonymization feature **never activates**
- `create_snapshot_context()` calls `scrub_snapshot()` at line 1208 **without export_salt parameter**
- Function signature doesn't even accept export_salt
- Feature is dead code - tests pass but feature doesn't work

**Fix Required**:
```python
def create_snapshot_context(..., export_salt: bytes | None = None) -> SnapshotContext:
    # ...
    scrub_summary = scrub_snapshot(snap_db, export_salt=export_salt)
```

**Impact**: Entire pseudonymization feature non-functional. Blocking PR #40 merge.

---

### Bug 2: Missing NULL Check for Agent Names ⚠️

**Location**: `src/mcp_agent_mail/share.py:746-757`

**Problem**:
- Copilot identified: If `agent.name` is NULL → `TypeError` on line 751
- F-string formatting fails: `f"{original_name}{export_salt.hex()}"`

**Fix Required**:
```python
for agent in agent_rows:
    agent_id = agent["id"]
    original_name = agent["name"]
    
    # Skip agents with NULL names
    if original_name is None:
        continue
    
    # ... rest of pseudonymization logic
```

---

## Action Items

1. Read PR #40 review comments from Cursor bot
2. Fix both bugs in share.py
3. Verify pseudonymization actually works with manual test
4. Run full test suite
5. Update PR #40

**Blocker**: PR #40 should NOT merge until these are fixed.

-m
