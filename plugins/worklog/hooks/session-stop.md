---
event: Stop
priority: 100
match_files: ["*"]
---

# Session Stop Hook - Worklog Learning Capture

Automatically capture learnings and log work completion when a session ends.

## Behavior by Profile

Read configuration from `~/.claude/worklog.local.md` frontmatter.

### Configuration Check

```bash
HOOK_MODE=$(grep -A1 "^hook_mode:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
PROFILE=$(grep -A1 "^profile:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
DB_PATH=$(grep -A1 "^db_path:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
SYSTEM_NAME=$(grep -A1 "^system_name:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')

DB_PATH="${DB_PATH/#\~/$HOME}"
```

### Stop Behavior Modes

| Mode | On Stop Behavior | Default For |
|------|------------------|-------------|
| `off` | Nothing | - |
| `remind` | Remind if significant work detected | minimal |
| `light` | Prompt to store if todos completed | standard |
| `full` | Auto-log session summary | full |
| `aggressive` | Auto-log + extract and store learnings | full (shared) |

## Execution

### Determining "Significant Work"

Check indicators of meaningful work:
1. **TodoWrite activity**: Were todos created and completed?
2. **File modifications**: Were files edited/created?
3. **Session length**: Did session involve multiple exchanges?

```bash
# This is determined by analyzing the conversation context
# The hook receives context about what occurred in the session
```

### Mode: off
Do nothing.

### Mode: remind

If significant work detected, output:
```
<worklog-reminder>
📝 Session had significant activity. Consider storing learnings:
- Use `memory-store` skill to capture reusable knowledge
- Key learnings persist across sessions
</worklog-reminder>
```

If trivial session, output nothing.

### Mode: light

If todos were completed during session:
```
<worklog-prompt>
## Session Summary

Completed tasks detected. Would you like to log this work?

**Suggested entry:**
```sql
INSERT INTO entries (agent, task_type, title, outcome, tags) VALUES
('{system_name}', '{inferred_type}', '{task_summary}', '{outcome_summary}', '{auto_tags}');
```

Reply "yes" to store, or provide corrections.
</worklog-prompt>
```

### Mode: full

Auto-log session summary (no user prompt needed):
```bash
# Extract session metadata
TASK_TYPE="{inferred from conversation}"
TITLE="{extracted task summary}"
OUTCOME="{completion status and key results}"
TAGS="system:$SYSTEM_NAME,agent:claude,session:$(date +%Y%m%d)"

# Log to database
sqlite3 "$DB_PATH" "INSERT INTO entries
(agent, task_type, title, details, outcome, tags) VALUES
('$SYSTEM_NAME', '$TASK_TYPE', '$TITLE',
'{session_details}', '$OUTCOME', '$TAGS');" 2>/dev/null
```

Output confirmation:
```
<worklog-logged>
✅ Session logged to worklog.
- Type: {task_type}
- Title: {title}
- Outcome: {outcome}
</worklog-logged>
```

### Mode: aggressive

Everything in `full` mode, PLUS:

1. **Extract learnings** from conversation and auto-store to knowledge_base:
```bash
# If reusable patterns/solutions were discussed
sqlite3 "$DB_PATH" "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system) VALUES
('{category}', '{learning_title}', '{learning_content}',
'{tags}', '$SYSTEM_NAME', '$SYSTEM_NAME');" 2>/dev/null
```

2. **Log errors resolved** to error_patterns:
```bash
# If errors were debugged and solved
sqlite3 "$DB_PATH" "INSERT INTO error_patterns
(error_signature, error_message, root_cause, resolution, tags) VALUES
('{signature}', '{error}', '{cause}', '{fix}', '{tags}');" 2>/dev/null
```

3. **Update memories** with session context:
```bash
# Store working context for next session
sqlite3 "$DB_PATH" "INSERT OR REPLACE INTO memories
(key, content, summary, memory_type, importance, source_agent, tags, status) VALUES
('ctx_${SYSTEM_NAME}_$(date +%Y%m%d)_session',
'{session_context}', '{one_line_summary}',
'context', 6, '$SYSTEM_NAME', '{tags}', 'staging');" 2>/dev/null
```

Output:
```
<worklog-logged mode="aggressive">
✅ Session auto-logged:
- Entry: {title}
- Learnings extracted: {count}
- Errors documented: {count}
- Context updated: {memory_key}

Knowledge compounds across sessions.
</worklog-logged>
```

## What Gets Extracted (aggressive mode)

### For knowledge_base
- Solutions to problems ("Here's how to fix X")
- Patterns discovered ("This pattern works well for Y")
- Commands/configurations that worked
- Gotchas and anti-patterns

### For error_patterns
- Errors that were debugged
- Root cause identified
- Resolution applied
- Prevention tips

### For memories
- Current project state
- Decisions made
- Next steps identified
- Blockers encountered

## Error Handling

If database write fails:
```
<worklog-warning>
⚠️ Could not log to worklog database.
Session summary (save manually if needed):
- Task: {title}
- Outcome: {outcome}

Run `/worklog-status` to check connectivity.
</worklog-warning>
```

## Notes

- Hook analyzes conversation context to determine what to log
- Aggressive mode uses LLM to extract structured learnings
- All auto-logged entries are tagged with `auto:true` for filtering
- User can always manually store with more detail via skills
- Network database failures gracefully degrade to `remind` mode
