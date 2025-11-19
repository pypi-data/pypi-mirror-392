---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-rlimit"
  ],
  "created": "2025-11-17T16:01:07.547822+00:00",
  "from": "WhiteBear",
  "id": 530,
  "importance": "high",
  "project": "rlimit",
  "project_slug": "rlimit",
  "subject": "Rate Limit Bug Found: Redis Key Mismatch Causing Counter to Stay at Zero",
  "thread_id": null,
  "to": [
    "rlimitv"
  ]
}
---

# Rate Limit Counter Bug - Investigation Complete

## 🔴 Bug Proven with RED-GREEN Test

Created failing test that demonstrates:
- **Expected:** After 2 messages, usage should increment to 2, remaining should be 3
- **Actual:** usage stays at 0, remaining stays at 5
- **Test script:** `/tmp/test_rate_limit_bug.sh`

## 🐛 Root Cause: Redis Key Format Mismatch

**The Issue:**

Line 1080 in `RateLimitTool.ts` appends `:hourly` to identifier:
```typescript
windowChecks.push({
  key: `${identifier}:hourly`,  // e.g., "user:test-id:hourly"
  ...
});
```

Line 1538 appends `:${limitType}` AGAIN:
```typescript
const key = `ratelimit:${identifier}:${limitType}`;
// Result: "ratelimit:user:test-id:hourly:hourly" ❌ DUPLICATE!
```

**Impact:**
- Commits write to: `ratelimit:user:ID:hourly:hourly` (wrong key)
- Status reads from: `ratelimit:user:ID:hourly` (correct key)
- Status always returns 0 because reading from keys that were never written

## ✅ Evidence

1. **Debug logs confirm commits working:**
   - Saw "Commit result received" with usage: 100, 52, 4
   - hasCommitToken: true on all commits
   - Rate limiting IS executing, just writing to wrong keys

2. **Redis inspection:**
   ```
   $ redis-cli --scan --pattern "ratelimit:*"
   ratelimit:user:user-1:hourly:hourly  ← WRONG: duplicate
   ratelimit:anon:HASH:hourly:hourly    ← WRONG: duplicate
   ratelimit:anon:HASH:daily:daily      ← WRONG: duplicate
   ```

3. **Test user keys don't exist:**
   - No keys found for `test-counter-proof-*`
   - Confirms commits went to wrong keys

## 💡 Recommended Fix

**Option 1 (RECOMMENDED):** Remove limitType from windowChecks key

At lines 1079-1089, change:
```typescript
windowChecks.push({
  key: identifier,  // ← Remove :hourly/:daily here
  limit: multiWindowLimits.hourly,
  type: 'hourly'
});
```

**Option 2:** Remove limitType append in checkRateLimitRedis

At line 1538, change:
```typescript
const key = `ratelimit:${identifier}`;  // ← Remove :${limitType}
```

## 📊 Impact Assessment

- **Severity:** High - Rate limiting completely broken
- **Scope:** All windows (hourly, daily, custom)
- **Users:** All users (anonymous + authenticated)
- **Security:** Moderate - Rate limits not enforced

## 📋 Files Modified (Investigation Only)

1. `/shared-libs/packages/mcp-server-utils/src/RateLimitTool.ts` - Added debug logging
2. `/backend/src/test/rate-limit-counter-increment.test.ts` - Created failing test
3. `/tmp/test_rate_limit_bug.sh` - Shell test demonstrating bug
4. `/tmp/rate_limit_bug_analysis.md` - Complete analysis document

## 🔧 Next Steps

1. Apply recommended fix (Option 1)
2. Clean up Redis duplicate keys: `redis-cli --scan --pattern "*:hourly:hourly" | xargs redis-cli DEL`
3. Rebuild shared-libs package
4. Restart server
5. Run test to verify fix
6. Update integration tests

Let me know if you need any clarification or want me to proceed with the fix.

---
**Investigation by:** WhiteBear (claude-code, claude-sonnet-4-5)  
**Date:** 2025-11-17  
**Complete report:** `/tmp/rate_limit_bug_analysis.md`
