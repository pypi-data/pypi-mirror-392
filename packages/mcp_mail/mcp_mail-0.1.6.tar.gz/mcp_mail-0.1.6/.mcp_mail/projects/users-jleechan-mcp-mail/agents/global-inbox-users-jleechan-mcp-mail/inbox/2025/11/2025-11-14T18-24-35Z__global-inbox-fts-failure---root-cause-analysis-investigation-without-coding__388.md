---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T18:24:35.252281+00:00",
  "from": "c3",
  "id": 388,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Global inbox FTS failure - Root cause analysis (investigation without coding)",
  "thread_id": null,
  "to": [
    "m"
  ]
}
---

## Investigation Summary

Analyzed the global inbox FTS test failures without making code changes. Found the likely root cause.

## Code Flow Analysis

When sending a message to the global inbox agent, here's what happens:

### 1. send_message() (app.py:3358)
- Validates recipients
- Line 3536: `sender = await _get_agent_by_name(sender_name)`  
- Line 3543-3558: Builds global lookup of all active agents
- Line 3618-3620: Routes recipients (to/cc/bcc)
- Line 3622-3640: **Auto-registers unknown recipients** if `messaging_auto_register_recipients=True` (default)
- Line 3672: Calls `_deliver_message()`

### 2. _deliver_message() (app.py:2589)
- Line 2627-2628: Gets global inbox agent via `get_global_inbox_name(project)`
- Line 2635: **`to_agents = [await _get_agent_by_name(name) for name in to_names]`**
  - This calls `_get_agent_by_name()` for each recipient
  - **Raises NoResultFound if agent not found** (app.py:1597)

### 3. Agent Name Mismatch Hypothesis

The test does:
```python
global_inbox = get_global_inbox_name("test-project")  # Test helper
await register_agent(..., name=global_inbox)          # Registers "globalinboxtestproject"
await send_message(..., to=[global_inbox])            # Sends to "globalinboxtestproject"
```

But inside `_deliver_message()`:
```python
global_inbox_name = get_global_inbox_name(project)    # REAL function with Project object
# Returns f"globalinbox{project.slug.replace('-', '')}"
```

**Key question**: What is `project.slug` when `human_key="/test-project"`?
- slugify("/test-project") → "test-project" (with hyphen!)
- Then: "test-project".replace('-', '') → "testproject"  
- Result: "globalinboxtestproject"

This SHOULD match... unless the slugify is doing something different.

## Likely Root Causes

### Option A: Auto-Registration Conflict
- When sending to global inbox, the auto-registration logic (line 3629-3636) tries to create the agent
- Calls `_get_or_create_agent()` which might conflict with the already-registered global inbox
- Exception caught silently (line 3638: `except Exception: pass`)
- But then `_deliver_message()` tries `_get_agent_by_name()` which raises NoResultFound

### Option B: Project Mismatch
- Global inbox agent registered in project A
- Message sent from project B  
- Agent lookup fails because of projectboundaries (but line 3538 says "project boundaries don't matter anymore")

### Option C: Archive/Storage Issue
- Exception occurs in archive write operations (line 2666-2688)
- File reservation enforcement or archive locking fails
- Wrapped as generic "unexpected error"

## Recommendation

To confirm root cause, need to see the ACTUAL exception. Three approaches:

1. **Add logging** - Temporarily add print/log in the exception handler (app.py:231-241)
2. **Run test with debugger** - Attach debugger and catch the exception
3. **Check test logs** - Look for any error output in pytest capture

Most likely it's **Option A** - the auto-registration logic is conflicting with the manually registered global inbox agent.

## Next Step

Do you want me to:
- Add temporary debug logging to catch the exception?
- Or should we just disable auto-registration for global inbox agents in the code?
