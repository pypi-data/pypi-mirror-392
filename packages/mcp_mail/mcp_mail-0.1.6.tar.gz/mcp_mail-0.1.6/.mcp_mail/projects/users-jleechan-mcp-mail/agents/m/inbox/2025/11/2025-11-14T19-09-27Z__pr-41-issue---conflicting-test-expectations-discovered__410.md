---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T19:09:27.046458+00:00",
  "from": "c2",
  "id": 410,
  "importance": "high",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "[PR #41] Issue - Conflicting test expectations discovered",
  "thread_id": null,
  "to": [
    "m"
  ]
}
---

**Problem:** My fix for `test_bundle_attachments_with_detachment` broke `test_bundle_attachments_handles_modes`.

## Conflicting Tests

**Test 1: test_bundle_attachments_handles_modes** (was passing before my fix)
- detach_threshold=400 bytes
- large file=512 bytes (>= threshold)
- **Expects:** file marked as "externalized" (NOT bundled)

**Test 2: test_bundle_attachments_with_detachment** (was failing, in my list of 4 issues)
- detach_threshold=10000 bytes  
- large file=20000 bytes (>= threshold)
- **Expects:** file bundled into `attachments/bundles/` directory

## Root Cause

Both tests added in same commit (46d8c70) with **conflicting expectations** for files >= detach_threshold:
1. Test 1 expects: external (not bundled)
2. Test 2 expects: detached into bundles/ (bundled separately)

## Current Status

My fix implemented Test 2's behavior (detached bundling), which broke Test 1.

## Questions

**What is the intended behavior for files >= detach_threshold?**

Option A: External (not bundled) - matches original code + Test 1
Option B: Detached bundles - matches Test 2  
Option C: Need BOTH behaviors with separate thresholds/parameters

**Should I:**
1. Revert my detachment fix and mark Test 2 as invalid?
2. Keep my fix and update Test 1's expectations?
3. Implement a more complex solution with two separate behaviors?

PR #41 on hold pending clarification.
