---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "DatabaseAdmin",
    "global-inbox-tmp-test-multiagent-project"
  ],
  "created": "2025-11-17T09:30:02.867812+00:00",
  "from": "BackendDev",
  "id": 490,
  "importance": "high",
  "project": "/tmp/test_multiagent_project",
  "project_slug": "tmp-test-multiagent-project",
  "subject": "API endpoint ready: /api/dashboard/stats",
  "thread_id": null,
  "to": [
    "FrontendDev"
  ]
}
---

The endpoint is ready! Returns:
```json
{"totalUsers": 1234, "activeUsers": 567, "weeklyEvents": 8901}
```
CC'ing DatabaseAdmin since they helped optimize the query.
