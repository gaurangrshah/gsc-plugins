---
name: memory-store
description: Store knowledge, entries, errors, and context in the worklog database using direct SQL
---

# Memory Store Skill

Store information in the worklog database for cross-session persistence.

## Prerequisites

- Worklog plugin configured (run `/worklog-init` or `/worklog-connect` first)
- Database path from `.claude/worklog.local.md`

## What to Store

### DO Store

| Type | Table | When |
|------|-------|------|
| Reusable learnings | `knowledge_base` | Patterns, gotchas, anti-patterns |
| Work completion | `entries` | After significant tasks |
| Error resolutions | `error_patterns` | When you solve a tricky error |
| Working context | `memories` | Session state, decisions in progress |
| Issues found | `issues` | Bugs, problems to track |

### DO NOT Store

| Type | Why Not | Alternative |
|------|---------|-------------|
| In-progress tasks | Transient | Use TodoWrite |
| Obvious code behavior | Documented in code | None needed |
| Already in files | Redundant | Reference the file |
| Trivial changes | No reuse value | None needed |

## Store Patterns

### Knowledge Base Entry

For reusable learnings, patterns, protocols:

```bash
sqlite3 {db_path} "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system) VALUES (
'{category}',
'{title}',
'{content}',
'{tags}',
'{agent_name}',
'{system_name}'
);"
```

**Categories:** `system-administration`, `development`, `infrastructure`, `decisions`, `projects`, `protocols`

**Content format:**
```
**Problem:** What was the issue

**Solution:** How to solve it

**Commands:**
\`\`\`bash
example commands
\`\`\`

**Notes:** Gotchas, warnings
```

### Work Entry

For logging completed work:

```bash
sqlite3 {db_path} "INSERT INTO entries
(agent, task_type, title, details, decision_rationale, outcome, tags, related_files) VALUES (
'{agent_name}',
'{task_type}',
'{title}',
'{details}',
'{why_this_approach}',
'{outcome}',
'{tags}',
'{related_files}'
);"
```

**Task types:** `configuration`, `deployment`, `debugging`, `documentation`, `research`, `maintenance`, `development`

### Error Pattern

For error resolutions:

```bash
sqlite3 {db_path} "INSERT INTO error_patterns
(error_signature, error_message, platform, language, root_cause, resolution, prevention_tip, tags) VALUES (
'{signature_regex_or_key_text}',
'{full_error_message}',
'{platform}',
'{language}',
'{root_cause}',
'{resolution}',
'{prevention_tip}',
'{tags}'
);"
```

**Platforms:** `linux`, `macos`, `docker`, `nas`, `all`
**Languages:** `python`, `typescript`, `bash`, `go`, `rust`, `all`

### Memory (Working Context)

For session state and context:

```bash
sqlite3 {db_path} "INSERT INTO memories
(key, content, summary, memory_type, importance, source_agent, system, tags) VALUES (
'{unique_key}',
'{content}',
'{one_line_summary}',
'{memory_type}',
{importance_1_to_10},
'{agent_name}',
'{system_name}',
'{tags}'
);"
```

**Memory types:** `fact`, `entity`, `preference`, `context`
**Key format:** `{type}_{agent}_{date}_{slug}` (e.g., `ctx_jarvis_20251213_webgen_review`)

### Issue

For tracking problems:

```bash
sqlite3 {db_path} "INSERT INTO issues
(project, title, description, status, tags, source_agent) VALUES (
'{project_name}',
'{issue_title}',
'{description}',
'open',
'{tags}',
'{agent_name}'
);"
```

## Tagging Convention

Always include structured tags:

```
system:{system_name},agent:{agent_name},topic:{topic1},topic:{topic2}
```

Examples:
- `system:my-laptop,agent:claude,topic:docker,topic:networking`
- `system:shared,agent:claude,type:protocol,topic:sqlite`

## Network Retry Logic

For shared databases, wrap writes in retry logic:

```bash
for i in 1 2 3; do
  sqlite3 {db_path} "YOUR SQL HERE" && break
  echo "Attempt $i failed, waiting..."
  sleep $((5 + RANDOM % 6))
done
```

## Examples

### Store a learning

```bash
sqlite3 ~/.claude/worklog/worklog.db "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system) VALUES (
'development',
'React useEffect cleanup pattern',
'**Problem:** Memory leaks from uncleared intervals

**Solution:** Return cleanup function from useEffect

**Code:**
\`\`\`typescript
useEffect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id);
}, []);
\`\`\`

**Notes:** Also applies to event listeners, subscriptions',
'system:shared,agent:claude,topic:react,topic:hooks,type:pattern',
'claude',
'$(hostname)'
);"
```

### Log completed work

```bash
sqlite3 ~/.claude/worklog/worklog.db "INSERT INTO entries
(agent, task_type, title, details, outcome, tags) VALUES (
'claude',
'development',
'Implemented worklog plugin',
'Created plugin structure, commands, skills, and templates',
'Plugin ready for testing',
'system:$(hostname),agent:claude,project:worklog-plugin'
);"
```
