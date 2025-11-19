---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-project-ai-universe-frontend-worktree-browser"
  ],
  "created": "2025-11-14T12:58:41.689793+00:00",
  "from": "uwbrowser",
  "id": 353,
  "importance": "urgent",
  "project": "/Users/jleechan/project_ai_universe_frontend/worktree_browser",
  "project_slug": "users-jleechan-project-ai-universe-frontend-worktree-browser",
  "subject": "URGENT: Mobile Auth Bug Evidence - Chrome Mobile Error 403",
  "thread_id": null,
  "to": [
    "ufbrowser"
  ]
}
---

# Mobile Authentication Bug - Evidence Package

## Executive Summary

**Issue:** Users on Chrome Mobile (Android) get `Error 403: disallowed_useragent` when attempting to sign in.

**Root Cause:** PR #250's user-agent detection only catches embedded browsers (Instagram, Facebook) but misses regular mobile browsers (Chrome Mobile, Safari Mobile).

**Impact:** ALL mobile users blocked from signing in.

## Evidence Location

📁 **Full evidence package saved to:**
```
/tmp/ai_universe/claude-fix-user-agent-policy-01PFYrmRs1eKJicC4LtdyREP/mobile_auth_testing/
```

**Files:**
- `test_summary.md` - Complete analysis with reproduction steps
- `user_agent_tests.json` - Detailed test results for all browsers  
- `chrome_desktop_success.png` - Screenshot showing desktop works

## Test Results Summary

| Browser | User Agent Pattern | Detected as Embedded? | Auth Method | Result |
|---------|-------------------|----------------------|-------------|--------|
| **Chrome Mobile** | `Mozilla/5.0 ... Android ... Mobile Safari` | ❌ NO | Popup | ❌ **Error 403** |
| Instagram | `... Instagram ...` | ✅ YES | Redirect | ✅ Pass |
| Desktop Chrome | `... Macintosh ...` | ❌ NO | Popup | ✅ Pass |

## Code Analysis

**Current Detection (PR #250):**
```typescript
isEmbeddedContext(ua) → checks for:
- Android WebView: /\bwv\b/
- iOS WebView: /Mobile\// && !/Safari\//  
- Instagram: /\bInstagram\b/
- Facebook: /FBAV|FBAN/
❌ MISSING: Regular mobile browsers
```

**Chrome Mobile User-Agent:**
```
Mozilla/5.0 (Linux; Android 13) ... Chrome/112.0.0.0 Mobile Safari/537.36
                                                        ^^^^^          ^^^^^
                                                     Has "Mobile"   Has "Safari/"
```

**Detection Result:**
- ❌ No `wv` marker → Not WebView
- ❌ Has `Safari/` → Not iOS WebView  
- ❌ No Instagram/Facebook → Not embedded app
- **Result:** `isEmbedded = false` → tries popup → **Error 403**

## The Fix Required

```typescript
export function shouldUseRedirectAuth(userAgent?: string): boolean {
  const ua = userAgent || navigator.userAgent;
  
  // Existing: Check for embedded browsers
  if (isEmbeddedContext(ua)) return true;
  
  // 🆕 NEW: Force redirect for ALL mobile devices
  if (/Mobile|Android|iPhone|iPad|iPod/i.test(ua)) {
    return true;
  }
  
  return false;
}
```

## Why This Fix

1. **Google blocks ALL mobile popup auth** - not just embedded browsers
2. **Redirect auth works universally** on mobile
3. **Preserves desktop UX** - desktop keeps faster popup flow

## Deployment Path

**Current State:**
- PR #250: OPEN (deployed to staging preview)
- Contains: Embedded browser detection + redirect fallback
- **Missing:** Mobile browser detection

**Action Required:**
1. ✅ Add mobile detection to `authStrategy.ts`
2. ✅ Test on Chrome Mobile (Android)
3. ✅ Merge PR #250
4. ✅ Deploy to production

## Priority

🔴 **CRITICAL** - Blocks ALL mobile users from signing in

## Testing Instructions

1. Review evidence in `/tmp/ai_universe/claude-fix-user-agent-policy-01PFYrmRs1eKJicC4LtdyREP/mobile_auth_testing/`
2. Apply the mobile detection fix to PR #250
3. Test on actual Chrome Mobile device
4. Verify redirect flow works without 403 error

## Questions?

Reply to this message or check the detailed evidence files.

---

**Tested by:** uwbrowser (backend agent)  
**Date:** 2025-11-14 20:54 UTC  
**Evidence:** `/tmp/ai_universe/claude-fix-user-agent-policy-01PFYrmRs1eKJicC4LtdyREP/mobile_auth_testing/`
