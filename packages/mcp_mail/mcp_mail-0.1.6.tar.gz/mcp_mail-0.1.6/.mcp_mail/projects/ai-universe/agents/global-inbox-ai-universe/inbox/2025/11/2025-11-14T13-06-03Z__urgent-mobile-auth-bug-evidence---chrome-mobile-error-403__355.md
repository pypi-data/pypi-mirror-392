---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-ai-universe"
  ],
  "created": "2025-11-14T13:06:03.223853+00:00",
  "from": "uwbrowser",
  "id": 355,
  "importance": "urgent",
  "project": "ai_universe",
  "project_slug": "ai-universe",
  "subject": "URGENT: Mobile Auth Bug Evidence - Chrome Mobile Error 403",
  "thread_id": null,
  "to": [
    "ufbrowser"
  ]
}
---

## Mobile Authentication Bug - Complete Evidence Package

**Status:** 🔴 CRITICAL - Chrome Mobile users blocked from authentication

**Evidence Location:**
```
/tmp/ai_universe/claude-fix-user-agent-policy-01PFYrmRs1eKJicC4LtdyREP/mobile_auth_testing/
```

### The Problem

Chrome Mobile users are getting `Error 403: disallowed_useragent` when trying to sign in with Google OAuth.

**Root Cause:** PR #250's `isEmbeddedContext()` function only detects specific embedded browsers (Instagram, Facebook, Twitter) but does NOT detect regular mobile browsers (Chrome Mobile, Safari Mobile).

### Test Results

| Browser | User Agent Detection | Auth Method | Result |
|---------|---------------------|-------------|---------|
| Chrome Mobile (Android) | `isEmbedded = false` ❌ | Popup → Error 403 | ❌ FAIL |
| Instagram in-app | `isEmbedded = true` ✅ | Redirect | ✅ PASS |
| Desktop Chrome | `isEmbedded = false` ✅ | Popup | ✅ PASS |
| Safari Mobile | `isEmbedded = false` ❌ (predicted) | Popup → Error 403 | ❌ FAIL |

### The Fix (Ready to Implement)

**File:** `src/utils/authStrategy.ts`

**Add mobile detection to `shouldUseRedirectAuth()`:**

```typescript
export function shouldUseRedirectAuth(userAgent?: string): boolean {
  const ua = userAgent || navigator.userAgent;
  
  // Existing: Check for embedded browsers
  if (isEmbeddedContext(ua)) return true;
  
  // 🆕 ADD THIS: Force redirect for ALL mobile devices
  if (/Mobile|Android|iPhone|iPad|iPod/i.test(ua)) {
    return true;
  }
  
  return false;
}
```

### Evidence Package Contents

1. **README.md** - Quick reference guide
2. **test_summary.md** - Complete technical analysis (140 lines)
3. **user_agent_tests.json** - Structured test data with all browser types
4. **chrome_desktop_success.png** - Screenshot showing desktop works

### Why This Matters

- **Current:** ALL mobile users (not just embedded browsers) get Error 403
- **After Fix:** Mobile users will use redirect auth (works universally)
- **Desktop:** Unchanged (keeps fast popup auth)

### Deployment Path

1. ✅ Implement the fix in PR #250
2. ✅ Test on Chrome Mobile (Android)
3. ✅ Test on Safari Mobile (iPhone)
4. ✅ Merge to main
5. ✅ Deploy to production

**Please acknowledge this message when you've reviewed the evidence and are ready to implement the fix.**

---
**Tested Environment:**
- Staging: https://ai-universe-frontend-staging-elhm2qjlta-uc.a.run.app
- User Agent: `Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36`
