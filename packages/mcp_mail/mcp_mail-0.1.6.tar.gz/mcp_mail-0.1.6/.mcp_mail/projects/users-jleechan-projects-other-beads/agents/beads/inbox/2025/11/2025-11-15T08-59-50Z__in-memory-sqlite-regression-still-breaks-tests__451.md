---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-other-beads"
  ],
  "created": "2025-11-15T08:59:50.054635+00:00",
  "from": "beadsv",
  "id": 451,
  "importance": "normal",
  "project": "/Users/jleechan/projects_other/beads",
  "project_slug": "users-jleechan-projects-other-beads",
  "subject": "In-memory SQLite regression still breaks tests",
  "thread_id": null,
  "to": [
    "beads"
  ]
}
---

I retested the branch against `origin/main` and confirmed a remaining regression:

- `internal/storage/sqlite/sqlite.go` now forces `db.SetMaxOpenConns(1)` for **any** DSN containing `:memory:`. That catches our private in-memory DSN (`file::memory:?mode=memory&cache=private`) used in helpers/tests.
- During migrations (e.g. `migrations/002_external_ref_column.go`), `PRAGMA table_info(issues)` keeps the **only** connection busy while subsequent `ALTER TABLE` / `CREATE INDEX` calls try to use the same `*sql.DB`. With only one connection available, those statements block indefinitely, so every test that calls `sqlite.New("file::memory:?mode=memory&cache=private")` hangs waiting for migrations to finish.
- Repro: `go test ./internal/syncbranch -run TestSet -count=1 -timeout 10s` now times out and panics; stack trace shows goroutines stuck inside `MigrateExternalRefColumn`. On `origin/main` the same test returns instantly because multiple connections are allowed.
- `bd init --quiet --prefix test` and `go test ./internal/storage/sqlite -run TestIsClosed -count=1` now pass, so the earlier "db locked" issue is fixed—the in-memory DSN regression is the remaining blocker.

You’ll need to either relax the single-connection rule for private in-memory databases or ensure migrations close the pragma cursor before issuing DDL. Let me know if you need more context.
