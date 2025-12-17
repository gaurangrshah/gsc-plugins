---
event: Stop
priority: 100
match_files: ["*"]
---

# Session Stop Hook - Worklog Learning Capture

Automatically capture learnings and log work completion when a session ends using **AI compression** - extract semantic learnings from raw session activity.

## AI Compression Pattern

Inspired by claude-mem's approach to knowledge extraction:

| Raw Data | Compressed Output | Storage |
|----------|-------------------|---------|
| Full conversation transcript | 1-2 sentence summary | entries.outcome |
| Debugging steps taken | Root cause + resolution | error_patterns |
| Decisions discussed | Decision + rationale | knowledge_base |
| Patterns observed | Pattern + when to apply | knowledge_base |
| Current work state | Context for resumption | memories |

**Why:** Raw transcripts waste tokens and storage. Semantic extraction preserves value, discards noise.

## Behavior by Hook Mode

Read configuration from `~/.claude/worklog.local.md` frontmatter.

### Configuration Check

```bash
HOOK_MODE=$(grep -A1 "^hook_mode:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
PROFILE=$(grep -A1 "^profile:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
DB_PATH=$(grep -A1 "^db_path:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')
SYSTEM_NAME=$(grep -A1 "^system_name:" ~/.claude/worklog.local.md 2>/dev/null | tail -1 | tr -d ' ')

DB_PATH="${DB_PATH/#\~/$HOME}"
SYSTEM_NAME="${SYSTEM_NAME:-$(hostname)}"
```

### Stop Behavior Modes

| Mode | On Stop Behavior | Compression | Default For |
|------|------------------|-------------|-------------|
| `off` | Nothing | None | - |
| `remind` | Remind if significant work | None | minimal |
| `light` | Prompt with compressed summary | Basic | standard |
| `full` | Auto-log compressed summary | Full | full |
| `aggressive` | Auto-log + extract all learnings | Deep | full (shared) |

## Determining "Significant Work"

Before any mode executes, assess session significance:

**Indicators of significant work:**
1. **TodoWrite activity**: Tasks created/completed during session
2. **File modifications**: Write/Edit tool used on project files
3. **Decisions made**: Architecture, implementation, or tool choices
4. **Problems solved**: Debugging, troubleshooting, fixes applied
5. **Session length**: Multiple exchanges (>5 user messages)

**Quick heuristic:**
```
SIGNIFICANT = (todos_completed > 0) OR
              (files_modified > 2) OR
              (session_messages > 10) OR
              (errors_resolved > 0)
```

If not significant, modes `remind` and `light` output nothing.

## Execution

### Mode: off

Do nothing.

### Mode: remind

If significant work detected, output reminder:
```
<worklog-reminder>
Session had significant activity. Consider capturing learnings:
- Use `memory-store` skill to save reusable knowledge
- Decisions and patterns persist across sessions
</worklog-reminder>
```

If trivial session, output nothing.

### Mode: light

**Step 1: Generate compressed summary**

Analyze session to produce:
```yaml
summary:
  title: "One-line description of work done"
  type: "development|debugging|research|configuration|documentation"
  outcome: "Completed|Partial|Blocked"
  key_result: "The main thing accomplished"
```

**Step 2: Present for confirmation**

```
<worklog-prompt mode="light">
## Session Summary (Compressed)

**Title:** {title}
**Type:** {type}
**Outcome:** {outcome}
**Key Result:** {key_result}

Store this to worklog? Reply:
- "yes" to store as-is
- "yes, also learned: <insight>" to add learning
- "no" to skip
</worklog-prompt>
```

**Step 3: If confirmed, store**

```bash
sqlite3 "$DB_PATH" "INSERT INTO entries
(agent, task_type, title, outcome, tags) VALUES
('$SYSTEM_NAME', '{type}', '{title}', '{key_result}',
'system:$SYSTEM_NAME,auto:light,session:$(date +%Y%m%d)');" 2>/dev/null
```

### Mode: full

**Step 1: Deep compression - extract structured data**

Analyze entire session to extract:

```yaml
session:
  # Entry for entries table
  entry:
    title: "Concise title of work performed"
    type: "development|debugging|research|configuration|documentation"
    details: "2-3 sentence description of what was done"
    outcome: "What was accomplished or current state"
    tags: ["auto-generated", "relevant", "tags"]

  # Context for memories table (for session resumption)
  context:
    current_state: "Where work stands now"
    next_steps: "What should happen next"
    blockers: "Any blockers identified"
    importance: 5-8  # Based on work significance
```

**Step 2: Auto-store (no confirmation needed)**

```bash
# Store entry
sqlite3 "$DB_PATH" "INSERT INTO entries
(agent, task_type, title, details, outcome, tags) VALUES
('$SYSTEM_NAME', '{type}', '{title}', '{details}', '{outcome}',
'system:$SYSTEM_NAME,auto:full,session:$(date +%Y%m%d),{additional_tags}');" 2>/dev/null

# Store/update session context memory
sqlite3 "$DB_PATH" "INSERT OR REPLACE INTO memories
(key, content, summary, memory_type, importance, source_agent, tags, status) VALUES
('ctx_${SYSTEM_NAME}_$(date +%Y%m%d)_session',
'{current_state}. Next: {next_steps}. {blockers}',
'{title}',
'context', {importance}, '$SYSTEM_NAME',
'session,auto:full,{tags}', 'staging');" 2>/dev/null
```

**Step 3: Output confirmation**

```
<worklog-logged mode="full">
Session logged:
- Entry: {title}
- Outcome: {outcome}
- Context saved for resumption

Use `memory-recall` to review stored context.
</worklog-logged>
```

### Mode: aggressive

Everything in `full` mode, PLUS deep extraction of all learning types.

**Step 1: Extract ALL learnable content**

```yaml
extraction:
  # Decisions made during session
  decisions:
    - title: "Decision title"
      choice: "What was decided"
      rationale: "Why this choice"
      alternatives: "What was considered"
      category: "architecture|implementation|tooling|process"

  # Patterns discovered or applied
  patterns:
    - title: "Pattern name"
      description: "What the pattern is"
      when_to_use: "Applicable situations"
      example: "Brief example from session"
      category: "design|code|workflow|debugging"

  # Errors debugged and resolved
  errors:
    - signature: "Error type/message pattern"
      message: "Actual error encountered"
      root_cause: "What caused it"
      resolution: "How it was fixed"
      prevention: "How to avoid in future"

  # Gotchas and anti-patterns
  gotchas:
    - title: "Gotcha description"
      wrong_approach: "What doesn't work"
      right_approach: "What to do instead"
      context: "When this applies"

  # Commands/configurations that worked
  commands:
    - command: "The command or config"
      purpose: "What it does"
      context: "When to use"
```

**Step 2: Store each extraction type**

```bash
# Store decisions to knowledge_base
for decision in decisions:
  sqlite3 "$DB_PATH" "INSERT INTO knowledge_base
  (category, title, content, tags, source_agent, system) VALUES
  ('decisions', '{decision.title}',
  'Decision: {decision.choice}\n\nRationale: {decision.rationale}\n\nAlternatives considered: {decision.alternatives}',
  '{decision.category},auto:aggressive,decision', '$SYSTEM_NAME', '$SYSTEM_NAME');" 2>/dev/null

# Store patterns to knowledge_base
for pattern in patterns:
  sqlite3 "$DB_PATH" "INSERT INTO knowledge_base
  (category, title, content, tags, source_agent, system) VALUES
  ('patterns', '{pattern.title}',
  '{pattern.description}\n\nWhen to use: {pattern.when_to_use}\n\nExample: {pattern.example}',
  '{pattern.category},auto:aggressive,pattern', '$SYSTEM_NAME', '$SYSTEM_NAME');" 2>/dev/null

# Store errors to error_patterns
for error in errors:
  sqlite3 "$DB_PATH" "INSERT INTO error_patterns
  (error_signature, error_message, root_cause, resolution, prevention, tags) VALUES
  ('{error.signature}', '{error.message}', '{error.root_cause}',
  '{error.resolution}', '{error.prevention}', 'auto:aggressive');" 2>/dev/null

# Store gotchas to knowledge_base
for gotcha in gotchas:
  sqlite3 "$DB_PATH" "INSERT INTO knowledge_base
  (category, title, content, tags, source_agent, system) VALUES
  ('gotchas', '{gotcha.title}',
  'Wrong: {gotcha.wrong_approach}\n\nRight: {gotcha.right_approach}\n\nContext: {gotcha.context}',
  'gotcha,anti-pattern,auto:aggressive', '$SYSTEM_NAME', '$SYSTEM_NAME');" 2>/dev/null
```

**Step 3: Output detailed confirmation**

```
<worklog-logged mode="aggressive">
Session fully processed:

**Entry:** {title}
**Outcome:** {outcome}

**Extracted & Stored:**
| Type | Count | Examples |
|------|-------|----------|
| Decisions | {decisions.length} | {decisions[0].title if any} |
| Patterns | {patterns.length} | {patterns[0].title if any} |
| Errors | {errors.length} | {errors[0].signature if any} |
| Gotchas | {gotchas.length} | {gotchas[0].title if any} |

**Context:** Saved for session resumption

Knowledge compounds across sessions. Query with `memory-recall`.
</worklog-logged>
```

## Compression Quality Guidelines

### What to Extract

| Type | Extract If... | Skip If... |
|------|---------------|------------|
| **Decisions** | Explicit choice made with rationale | Obvious/trivial choice |
| **Patterns** | Reusable across projects/sessions | One-time solution |
| **Errors** | Debugging took >5 minutes | Typo/obvious fix |
| **Gotchas** | Non-obvious, easy to forget | Well-documented elsewhere |
| **Commands** | Complex or rarely used | Common/well-known |

### Compression Ratios

Target compression:
- **Session transcript**: 10,000+ tokens → **Entry**: ~100 tokens
- **Debugging session**: 5,000 tokens → **Error pattern**: ~150 tokens
- **Decision discussion**: 2,000 tokens → **Decision record**: ~100 tokens

### Avoiding Duplicates

Before storing to knowledge_base, check for existing similar entries:

```bash
# Check for similar title
EXISTING=$(sqlite3 "$DB_PATH" "SELECT id FROM knowledge_base
WHERE title LIKE '%{similar_keywords}%' LIMIT 1;" 2>/dev/null)

if [ -n "$EXISTING" ]; then
  # Update existing instead of creating duplicate
  sqlite3 "$DB_PATH" "UPDATE knowledge_base
  SET content = content || '\n\n---\nAdditional context: {new_content}',
  updated_at = datetime('now')
  WHERE id = $EXISTING;" 2>/dev/null
fi
```

## Error Handling

**Database write fails:**
```
<worklog-warning>
Could not log to worklog database.

**Session summary (save manually):**
- Title: {title}
- Outcome: {outcome}
- Key learnings: {learnings_summary}

Run `/worklog-status` to check connectivity.
</worklog-warning>
```

**Network timeout:**
Gracefully degrade to `remind` mode and output summary for manual saving.

## Tagging Convention

All auto-logged entries include standard tags:

| Tag | Meaning |
|-----|---------|
| `auto:light` | Logged by light mode |
| `auto:full` | Logged by full mode |
| `auto:aggressive` | Logged by aggressive mode |
| `system:{hostname}` | Source system |
| `session:{YYYYMMDD}` | Session date |
| `type:{category}` | Content type |

This enables filtering: `SELECT * FROM entries WHERE tags LIKE '%auto:aggressive%'`

## Backwards Compatibility

- All existing hook_mode values work unchanged
- Output format enhanced but structurally similar
- Existing entries/knowledge_base queries unaffected
- No changes required to user configuration

## Notes

- Hook analyzes conversation context to determine extractions
- Compression uses LLM reasoning, not simple truncation
- All auto-logged entries tagged for easy identification/filtering
- Manual `memory-store` always available for more detail
- Network failures gracefully degrade to remind mode
- Duplicate detection prevents knowledge_base bloat

## Version History

### 1.3.0 (Current)
- **AI compression:** Semantic extraction vs raw logging
- **Deep extraction (aggressive):** Decisions, patterns, errors, gotchas
- **Duplicate detection:** Check before inserting to knowledge_base
- **Compression guidelines:** Clear rules for what to extract
- **Tagging convention:** Standard tags for filtering

### 1.2.0
- Initial hook modes (off, remind, light, full, aggressive)
- Basic session logging
