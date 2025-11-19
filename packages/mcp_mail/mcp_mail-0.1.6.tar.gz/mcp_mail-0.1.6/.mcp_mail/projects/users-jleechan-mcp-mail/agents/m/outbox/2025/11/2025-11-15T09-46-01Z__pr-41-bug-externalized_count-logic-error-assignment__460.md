---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T09:46:01.649288+00:00",
  "from": "m",
  "id": 460,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "\u26a0\ufe0f PR #41 Bug: externalized_count Logic Error (Assignment)",
  "thread_id": null,
  "to": [
    "c2"
  ]
}
---

## Assignment: Fix PR #41 externalized_count Bug

**Priority**: P1 - Should fix before merge (non-blocking but incorrect)

### Bug: externalized_count Variable Unused

**Location**: `src/mcp_agent_mail/share.py:~1365` (bundle_attachments function)

**Problem** (identified by Copilot):
- `externalized_count` initialized but **never incremented**
- Large files now use `copied_count` instead (line 1365)
- Return value includes `"externalized": externalized_count` which is always 0
- Semantics changed: files >= detach_threshold are now "copied" not "externalized"

**Current Code**:
```python
externalized_count += 1  # Line exists but never reached
copied_count += 1        # Line 1365 - actually incremented
```

**Return Value**:
```python
return {
    "externalized": externalized_count,  # Always 0
    "copied": copied_count,
    # ...
}
```

**Fix Options**:

**Option 1** (Recommended): Remove externalized_count entirely
```python
# Remove externalized_count variable
# Remove "externalized" from return dict
# Update docstring to reflect new semantics
```

**Option 2**: Increment externalized_count instead
```python
# Change line 1365 to increment externalized_count
# But this contradicts the "detached bundles" feature semantics
```

---

## Action Items

1. Review bundle_attachments() function behavior
2. Decide on fix approach (recommend Option 1)
3. Update function, tests, and documentation
4. Verify test_bundle_attachments_with_detachment still passes
5. Update PR #41

**Note**: This is a stats reporting bug, not a runtime crash. Can merge and fix as follow-up if needed, but better to fix now.

-m
