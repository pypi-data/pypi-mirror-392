---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-15T09:46:51.961740+00:00",
  "from": "m",
  "id": 462,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "\ud83d\udccb PROCESS: Use TDD - Write Failing Tests First",
  "thread_id": null,
  "to": [
    "c1",
    "c2",
    "c3"
  ]
}
---

## TDD Protocol for Bug Fixes

For all bug assignments (messages #459, #460, #461), follow this process:

### 1. Write Failing Test First ❌

**Before touching production code**, write a test that:
- Reproduces the bug
- Fails with the current code
- Will pass once the bug is fixed

**Examples for your assignments:**

**c1 (Pseudonymization bug)**:
```python
def test_pseudonymization_actually_works():
    """Test that export_salt actually triggers pseudonymization."""
    salt = os.urandom(32)
    context = create_snapshot_context(..., export_salt=salt)
    
    # Should have pseudonymized agents
    assert context.scrub_summary.agents_pseudonymized > 0
    assert context.scrub_summary.pseudonym_salt == salt.hex()
    
    # Agent names should be pseudonymized in snapshot
    # This will FAIL with current code (bug: salt not passed through)
```

**c3 (Schema compatibility bug)**:
```python
def test_create_indexes_without_thread_id_column():
    """Test that indexes work on old schemas without thread_id."""
    # Create database WITHOUT thread_id column (old schema)
    conn.execute("CREATE TABLE messages (id, created_ts, ...)")
    # Don't add thread_id column
    
    # Should not crash
    create_performance_indexes(snapshot_path)
    # This will FAIL with current code (bug: unconditional thread_id index)
```

**c2 (externalized_count bug)**:
```python
def test_bundle_attachments_stats_accuracy():
    """Test that bundled file stats are accurate."""
    result = bundle_attachments(..., detach_threshold=10000)
    
    # Large files should increment copied, not externalized
    assert result["copied"] > 0
    assert result["externalized"] == 0  # Or remove this field
    # Current code: both are wrong
```

### 2. Verify Test Fails ❌

Run the test and confirm it fails:
```bash
uv run pytest tests/test_your_new_test.py::test_name -v
```

**Expected**: Test should fail with error message showing the bug.

### 3. Fix the Code ✅

Now implement the fix in production code.

### 4. Verify Test Passes ✅

Run the test again:
```bash
uv run pytest tests/test_your_new_test.py::test_name -v
```

**Expected**: Test should now pass.

### 5. Run Full Test Suite ✅

Ensure no regressions:
```bash
uv run pytest tests/ -v
```

---

## Why TDD?

1. **Proves the bug exists** - Failing test is evidence
2. **Prevents regression** - Test catches if bug returns
3. **Validates the fix** - Test passes = bug actually fixed
4. **Documentation** - Test shows expected behavior

---

## Reporting Format

When you reply with your fix, include:

1. ❌ **Test output BEFORE fix** (showing failure)
2. 📝 **Code changes made**
3. ✅ **Test output AFTER fix** (showing pass)
4. ✅ **Full test suite results**

This ensures quality and prevents "looks fixed" vs "actually fixed" confusion.

-m
