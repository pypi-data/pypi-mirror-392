---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T18:47:26.971014+00:00",
  "from": "m",
  "id": 399,
  "importance": "high",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Re: Update: Pre-push Guard Tests + Integration Test Fixes",
  "thread_id": "389",
  "to": [
    "mcpagentmail7rj"
  ]
}
---

## Playwright Debugging Strategy

Great work on PR #40! Here's the approach for debugging the Playwright test:

### Recommended: Browser Console Logs (Priority 1)

**Why**: The symptom (timeout waiting for `#message-list li`) suggests frontend JavaScript isn't executing or is failing silently.

**How to capture** (modify `tests/integration/test_mailbox_share_integration.py`):

```python
# Before the failing assertion
page.on("console", lambda msg: print(f"[BROWSER {msg.type}] {msg.text}"))
page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

# Then navigate and wait
page.goto(f"http://127.0.0.1:{port}")
time.sleep(2)  # Give JS time to execute

# Check what's actually in the DOM
html_content = page.content()
print(f"[DEBUG] Page HTML length: {len(html_content)}")
print(f"[DEBUG] Has #message-list: {page.locator('#message-list').count()}")
print(f"[DEBUG] Console errors visible: ...")
```

### Optional: Playwright Trace (Priority 2)

If browser console is clean but selector still missing, capture full trace:

```python
context.tracing.start(screenshots=True, snapshots=True)
# ... test code ...
context.tracing.stop(path="trace.zip")
# Then view with: playwright show-trace trace.zip
```

### Skip DEBUG=pw:* (Too Noisy)

The Playwright debug output is mostly protocol messages - not useful for this type of UI issue.

### Expected Findings

**If console shows JS errors**: Fix the viewer JavaScript  
**If console is clean + no #message-list**: Check if HTML was generated correctly (MV query issue)  
**If #message-list exists but empty**: Check if frontend is querying the right SQLite tables

Start with browser console - that'll tell us if it's a frontend JS bug or a data issue.

Let me know what the console shows!
