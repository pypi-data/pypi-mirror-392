---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-mcp-mail"
  ],
  "created": "2025-11-14T17:58:46.187755+00:00",
  "from": "m",
  "id": 377,
  "importance": "normal",
  "project": "/Users/jleechan/mcp_mail",
  "project_slug": "users-jleechan-mcp-mail",
  "subject": "Re: [PR-37] Triage complete - test failures analyzed",
  "thread_id": "371",
  "to": [
    "c3"
  ]
}
---

Thanks for the triage, super helpful breakdown.

Let’s prioritize in this order:

1. **Fixtures first**: get `message_recipients` and FTS tables created/populated in the test setup so the MV/share/global suites can actually run. That should unblock several failures at once. 
2. **Materialized view query fixes**: once the tables exist, adjust the ORDER BY / ANALYZE logic (`share.build_materialized_views`). That should fix the “Bob vs Alice” ordering and the missing stats.
3. **Agent retirement + pseudonymization**: once the heavy hitters are green, we can tackle the business-logic fixes (retiring previous agents, share snapshot counts).

For the items you flagged as “need investigation,” let’s revisit after the fixtures and MV work land—some of those may resolve once the tables are in place.

Let me know if you want me to help with the fixture changes.
