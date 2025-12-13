<!-- WORKLOG_START -->
## Worklog Database (Minimal Profile)

**Database:** ${WORKLOG_DB_PATH}
**Profile:** minimal

### Usage

Store and recall cross-session knowledge using the worklog skills:

- **Store learnings:** Use `memory-store` skill after completing tasks with reusable insights
- **Recall context:** Use `memory-recall` skill when you need prior knowledge
- **Sync to docs:** Use `memory-sync` skill periodically to promote valuable entries

### Quick Reference

```bash
# Store knowledge
sqlite3 ${WORKLOG_DB_PATH} "INSERT INTO knowledge_base
(category, title, content, tags, source_agent) VALUES
('category', 'Title', 'Content', 'tags', 'agent-name');"

# Query knowledge
sqlite3 ${WORKLOG_DB_PATH} "SELECT title, content FROM knowledge_base
WHERE tags LIKE '%keyword%';"
```

### Tables Available

| Table | Purpose |
|-------|---------|
| `entries` | Work history |
| `knowledge_base` | Reusable learnings |
| `memories` | Working context |
| `issues` | Issue tracking |
| `error_patterns` | Error resolutions |
| `research` | External research |

Run `/worklog-status` to check connectivity.
<!-- WORKLOG_END -->
