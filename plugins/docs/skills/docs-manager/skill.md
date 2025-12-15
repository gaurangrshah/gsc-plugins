---
name: docs-manager
description: Maintain living documentation with single source of truth approach, journal reconciliation, and worklog.db integration
---

# Documentation Manager Skill

Maintain documentation using the single source of truth philosophy. All system documentation flows through one main guide file with inline updates.

## Prerequisites

- Environment variables configured (see Configuration below)
- Optional: Worklog plugin for cross-session persistence

## Configuration

Set these environment variables or create a local config file (e.g., `~/.claude/docs.local.md`):

```bash
# Required - set for your environment
DOCS_ROOT="${DOCS_ROOT:-~/docs}"
MAIN_GUIDE="${MAIN_GUIDE:-$DOCS_ROOT/guide.md}"
KNOWLEDGE_BASE="${KNOWLEDGE_BASE:-~/.claude/knowledge}"

# Optional - worklog integration (auto-detected if worklog plugin installed)
WORKLOG_DB="${WORKLOG_DB:-}"

# Optional - documentation query script
DOCS_QUERY_SCRIPT="${DOCS_QUERY_SCRIPT:-}"
```

### Example Configurations

**With Worklog Integration:**
```bash
DOCS_ROOT=~/docs
MAIN_GUIDE=~/docs/system-guide.md
KNOWLEDGE_BASE=~/.claude/knowledge
WORKLOG_DB=~/.claude/worklog/worklog.db
DOCS_QUERY_SCRIPT=~/scripts/query-docs.sh
```

**Shared Database (Multi-System):**
```bash
DOCS_ROOT=~/docs
MAIN_GUIDE=~/docs/system-guide.md
KNOWLEDGE_BASE=~/.claude/knowledge
WORKLOG_DB=/mnt/share/path/to/worklog.db  # Adjust to your mount path
DOCS_QUERY_SCRIPT=~/scripts/query-docs.sh
```

**Standalone (no worklog):**
```bash
DOCS_ROOT=~/docs
MAIN_GUIDE=~/docs/project-guide.md
KNOWLEDGE_BASE=~/.claude/knowledge
```

---

## Core Principle

> **ALL system documentation goes into your main guide (`$MAIN_GUIDE`)**
>
> Update it inline. NO separate files. NO exceptions.

---

## Working Documentation

### Use /tmp for Agent Process Work

**While working on tasks:**
- Use `/tmp/` for your own process notes, logs, investigation results
- Track your steps as you go
- Keep working files ephemeral (vanish on reboot)

**When task complete:**
- Review `/tmp/` working files
- Promote ONLY what's valuable to persistent locations
- Let everything else vanish

### When to Create Permanent Process Documentation

**✅ Create ONLY when:**
- Human needs to understand something they don't know
- Human needs to be communicated complex results/findings
- Human has expressed lack of knowledge requiring explanation
- It's actually necessary (not just "nice to have")

**❌ Don't create for:**
- Everything you do
- Your own reference
- "Documentation for documentation's sake"
- Things easily explained in a message

### Workflow

```bash
# 1. Use /tmp for your working notes
echo "Investigating issue X..." > /tmp/work-notes.md
# ... continue adding as you work ...

# 2. When done, review
cat /tmp/work-notes.md

# 3. Promote selectively:
# - System config changes → $MAIN_GUIDE (inline update)
# - Script automation → project scripts directory
# - Everything else → let it vanish

# 4. Default: Don't persist
```

**Rule:** Default to /tmp. Only persist when human actually needs it.

---

## When to Document

### ✅ ALWAYS Document (in $MAIN_GUIDE)

| Type | Where | When |
|------|-------|------|
| System config changes | $MAIN_GUIDE inline | Firewall, SSH, network changes |
| Service deployments | $MAIN_GUIDE inline | New services, modifications |
| Security changes | $MAIN_GUIDE + security/ | Any security-related change |
| Architectural decisions | `$KNOWLEDGE_BASE/decisions/` | Major design choices |
| Lessons learned | $MAIN_GUIDE "Key Lessons" | Gotchas, patterns discovered |

### ❌ NEVER Document

| Type | Why Not | Alternative |
|------|---------|-------------|
| Routine operations | No lasting value | None needed |
| Typo corrections | Trivial | Git commit message |
| Temporary investigations | Ephemeral | /tmp/ notes |
| Hypothetical configs | Not real | Wait until implemented |

**Rule:** If it changes system behavior or you'll need to reference it later → Document.

---

## Documentation Structure & Decision Tree

**CRITICAL: Before creating ANY .md file, follow this decision tree:**

```
1. Is this temporary work/planning?
   YES → /tmp/{task}-{date}.md (ephemeral)
   STOP

2. Is this system configuration?
   YES → $MAIN_GUIDE (inline update)
   STOP

3. Is this a cross-project pattern/decision/learning?
   YES → $KNOWLEDGE_BASE/
   ├─ decisions/ - Architecture decisions (ADRs)
   ├─ guides/ - Cross-project how-tos
   └─ learnings/ - Incident learnings
   STOP

4. Is this project-specific documentation?
   YES → $DOCS_ROOT/{category}/
   ├─ security/ - Security configs
   ├─ guides/ - How-to guides
   ├─ services/ - Service docs
   └─ audits/ - System audits
   STOP
```

### Forbidden Actions

**NEVER:**
- ❌ Create `$DOCS_ROOT/decisions/` directory (use `$KNOWLEDGE_BASE/decisions/`)
- ❌ Skip frontmatter on new documentation
- ❌ Create separate files for system config changes (use $MAIN_GUIDE)
- ❌ Leave /tmp files after task completion
- ❌ Create root-level .md files in $DOCS_ROOT (use subdirectories)

### Required Frontmatter

**ALL new documentation MUST include:**

```yaml
---
title: "Descriptive title"
type: decision|learning|guide|reference|audit|changelog|environment
created: YYYY-MM-DD
---
```

---

## How to Document

### Step 1: Open the Guide

```bash
# Edit the one true guide
$EDITOR $MAIN_GUIDE
```

### Step 2: Update Inline

**Find the relevant section:**
- Firewall change? → Update "Firewall" section
- SSH change? → Update "SSH" section
- New service? → Update "Services" section
- New lesson? → Add to relevant "Key Lessons" subsection

**Update these 3 places:**
1. **Relevant section** (add/modify configuration details)
2. **"Current State" table** (top of file)
3. **"Change History"** (bottom of file)

**Update header:**
- Change "Last Updated" date

### Step 3: Be Concise

**DO write:**
- Current configuration (what's active)
- How to access/use it
- Key lessons (1-2 sentences)
- Emergency procedures

**DON'T write:**
- Verbose explanations
- Hypothetical configurations
- Theoretical frameworks
- Template boilerplate

**Example - Good:**
```markdown
### Firewall
**Rules:** 2 (LAN + Tailscale)
**Lesson:** Firewall is inbound-only. No loopback/Docker rules needed.
```

**Example - Bad:**
```markdown
### Firewall Configuration Documentation

This section comprehensively documents the complete firewall
configuration strategy implemented across the system...

[10 paragraphs explaining obvious things]
```

---

## Anti-Patterns

### ❌ Creating Permanent Process Documentation Unnecessarily

**WRONG:**
```bash
# DON'T create permanent docs for agent work:
touch $DOCS_ROOT/how-i-fixed-docker-2025-11-08.md
touch ~/investigation-summary.md
touch ~/complete-fixes-summary.md
```

**RIGHT:**
```bash
# DO use /tmp for process work:
vi /tmp/docker-fix-notes.md
# Only persist if human actually needs it
```

### ❌ Creating Separate System Documentation Files

**WRONG:**
```bash
# DON'T do this:
touch $DOCS_ROOT/firewall-update-2025-11-08.md
touch $DOCS_ROOT/ssh-key-implementation.md
touch $DOCS_ROOT/docker-networking-fix.md
```

**RIGHT:**
```bash
# DO this:
$EDITOR $MAIN_GUIDE
# Update relevant section inline
```

### ❌ Over-Documenting

**WRONG:**
```markdown
## Firewall Rule Addition Procedure

### Prerequisites
- [ ] Understand network topology
- [ ] Review security policies
- [ ] Obtain change approval
...

### Step 1: Access Web Interface
Navigate to the control panel by opening your web browser
and entering the IP address... [500 more words]
```

**RIGHT:**
```markdown
### Firewall
Add rules: Web UI → Control Panel → Security → Firewall
```

### ❌ Keeping Stale Content

**WRONG:** Keeping old configuration details after they've changed

**RIGHT:** Update inline, note in Change History what changed

---

## Documentation Workflow

### For Material Changes

1. **Make the change** (firewall, SSH, service, etc.)
2. **Test it works**
3. **Open $MAIN_GUIDE**
4. **Update relevant section** (configuration details)
5. **Update "Current State" table** (if status changed)
6. **Add to "Change History"** (date, what, why)
7. **Update "Last Updated" date**
8. **Save and close**

**Time:** 2-5 minutes max

### For Lessons Learned

**If you discover a pattern or learn something important:**

1. **Find relevant section** (Firewall, SSH, Docker, etc.)
2. **Add to "Key Lessons" subsection** (1-2 sentences)
3. **Example:** "Firewall is inbound-only. No loopback rules needed."

### For New Systems

**If adding entirely new domain (rare):**

1. **Add new section** to $MAIN_GUIDE
2. **Follow existing format:** Current config → How to use → Lessons → Troubleshooting
3. **Keep it lean** (resist urge to add 50 pages)

---

## Quality Standards

### Good Documentation Has

- ✅ Current state clearly stated
- ✅ How to access/use it
- ✅ Key lessons (concise)
- ✅ Emergency procedures
- ✅ Change history entry

### Bad Documentation Has

- ❌ Hypothetical configurations
- ❌ Verbose explanations of obvious things
- ❌ Multiple files for same topic
- ❌ Outdated information
- ❌ Template boilerplate

---

## Examples

### Example 1: Firewall Rule Added

**Scenario:** "I added Tailscale to the firewall whitelist."

**Action:**
```markdown
# Open $MAIN_GUIDE

# 1. Update Firewall section:
### Current Configuration
Rules:
1. Allow local network (e.g., 192.168.x.0/24)
2. Allow VPN network (e.g., 100.64.0.0/10 for Tailscale)

# 2. Update Current State table:
| Firewall | ✅ ENABLED | 2 rules (LAN + VPN) |

# 3. Add to Change History:
### 2025-01-15
- Added VPN firewall rule

# 4. Update header:
Last Updated: 2025-01-15
```

**Time:** 2 minutes

### Example 2: Typo Fixed

**Scenario:** "Fixed typo in .zshrc comment."

**Action:** None. No documentation needed (non-material change).

### Example 3: Learning Discovered

**Scenario:** "TIL: Firewall is inbound-only."

**Action:**
```markdown
# Open $MAIN_GUIDE

# Add to Firewall → Key Lessons:
**Key insight:** Firewall is inbound-only.
No loopback or Docker rules needed.
```

**Time:** 30 seconds

---

## Integration Points

### With Git

Commit documentation changes with your project's git workflow:
```bash
git add $MAIN_GUIDE
git commit -m "docs: Update firewall configuration"
```

### With Knowledge Base

**$MAIN_GUIDE is for:**
- System configuration (what's active)
- How to use/access things
- Key lessons
- Troubleshooting

**$KNOWLEDGE_BASE is for:**
- Patterns across projects (not system-specific)
- Technical discoveries (language/tool quirks)
- Decision rationale (architecture choices)

**If in doubt:** Put it in $MAIN_GUIDE (safer)

---

## File Structure

```
$DOCS_ROOT/
├── README.md                    # Navigation hub and quick reference
├── {system}-guide.md            # THE GUIDE (single source of truth)
├── FRONTMATTER-SCHEMA.md        # Documentation standards
├── security/                    # ALL security documentation
│   ├── README.md
│   └── *.md
├── guides/                      # How-to guides and procedures
│   ├── README.md
│   └── *.md
├── services/                    # Service deployment documentation
│   ├── README.md
│   └── *.md
├── audits/                      # System audits and assessments
│   └── YYYY-MM-DD-*.md
├── archive/                     # Historical documentation (reference only)
│   └── *.md
└── baselines/                   # System state baselines
    └── current.json
```

**Documentation Guidelines:**

- **System configuration changes** → Update `$MAIN_GUIDE` inline
- **Security documentation** → Add to appropriate file in `security/`
- **How-to guides** → Add to `guides/` with frontmatter
- **Service deployments** → Document in `services/`
- **System audits** → Add to `audits/` with frontmatter
- **All documentation** → Use YAML frontmatter
- **Each subdirectory** → Has comprehensive README for navigation

**Never:**
- Create root-level .md files for incidents/changes (use $MAIN_GUIDE inline)
- Skip frontmatter on new documentation
- Bypass subdirectory READMEs (they provide important context)

---

## Maintenance

### Weekly

- Review $MAIN_GUIDE for accuracy
- Remove any bloat that crept in
- Verify "Current State" table is current

### After Every Change

- Update relevant section
- Update "Current State" if needed
- Add to "Change History"
- Update "Last Updated" date

### Never

- ❌ Create new documentation files for system changes
- ❌ Keep outdated information
- ❌ Add hypothetical configurations
- ❌ Write verbose explanations

---

## Success Criteria

**Good documentation system:**
- ✅ One file has everything
- ✅ Can find anything in <1 minute
- ✅ Current state always accurate
- ✅ No stale content
- ✅ No separate files

**Bad documentation system:**
- ❌ Multiple files per topic
- ❌ Can't find what you need
- ❌ Outdated information
- ❌ Documentation bloat
- ❌ Temporary files everywhere

---

## Frontmatter Standards

**All documentation uses YAML frontmatter for queryability**

### Required Fields

```yaml
---
title: "Brief descriptive title"
type: decision|learning|guide|reference|changelog|environment
created: YYYY-MM-DD
---
```

### Optional Fields

```yaml
updated: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: active|deprecated|superseded
category: "Primary category"
related: [path/to/doc.md]
commit: abc1234
environment: system-name
```

### Valid Type Values

| Type | Use Case |
|------|----------|
| `decision` | Architectural or operational decisions |
| `learning` | Lessons learned from incidents |
| `guide` | How-to documentation |
| `reference` | Reference docs and indexes |
| `changelog` | Change history |
| `environment` | Environment-specific docs |

### Document Templates

#### Decision Template (in $KNOWLEDGE_BASE/decisions/)

```markdown
---
title: "Decision title"
type: decision
category: infrastructure|security|tooling
tags: [relevant, tags]
status: active
created: YYYY-MM-DD
---

## Context
Why this decision was needed

## Decision
What was decided

## Rationale
- Reason 1
- Reason 2

## Consequences
**Positive:** What this enables
**Negative:** Trade-offs

## Alternatives Considered
- Option A: Why not
```

#### Learning Template (in $KNOWLEDGE_BASE/learnings/)

```markdown
---
title: "What we learned"
type: learning
category: incident|optimization|troubleshooting
tags: [relevant, tags]
created: YYYY-MM-DD
---

## What Happened
Situation description

## Root Cause
What caused it

## Solution
How resolved

## Prevention
How to avoid
```

#### Guide Template (in $KNOWLEDGE_BASE/guides/)

```markdown
---
title: "How to [do thing]"
type: guide
category: operations|security|maintenance
tags: [relevant, tags]
status: active
created: YYYY-MM-DD
---

## Purpose
What this accomplishes

## Prerequisites
What you need

## Steps
1. Step one
2. Step two

## Verification
How to verify

## Troubleshooting
Common issues
```

### Querying Documentation

If `$DOCS_QUERY_SCRIPT` is configured:

```bash
# Find security decisions
$DOCS_QUERY_SCRIPT --type decision --tag security

# Find recent learnings
$DOCS_QUERY_SCRIPT --type learning --updated-last 30d

# Find all guides
$DOCS_QUERY_SCRIPT --type guide --status active

# See all options
$DOCS_QUERY_SCRIPT --help
```

---

## Journal Reconciliation Workflow

**Purpose:** Convert agent journal notes into permanent documentation after task completion.

### When Invoked for Journal Reconciliation

When called with a journal file path (e.g., `/tmp/journal-fix-auth-2025-01-15.md`):

1. **Read and analyze the journal**
   - Parse all entry types (Discovery, Decision, Blocker, Checkpoint, Completed)
   - Identify what changed (code, config, architecture, services)
   - Extract key decisions and their rationale
   - Note any lessons learned or gotchas

2. **Determine documentation actions**
   Use this decision tree for each finding:

   ```
   Finding Type → Documentation Action
   ─────────────────────────────────────────────────────
   System config change     → Update $MAIN_GUIDE inline
   Service deployment       → Update services/ doc or $MAIN_GUIDE
   Security change          → Update security/ doc AND $MAIN_GUIDE
   Architecture decision    → Create/update $KNOWLEDGE_BASE/decisions/
   Lesson learned           → Add to relevant section's "Key Lessons"
   New pattern/approach     → Create $KNOWLEDGE_BASE/guides/ if cross-project
   Bug fix (non-trivial)    → Add to relevant troubleshooting section
   Code change only         → Update CHANGELOG only (if significant)
   Trivial change           → No documentation needed
   ```

3. **Execute documentation updates**
   For each required update:
   - Read the target file first
   - Make inline updates (never create separate incident files)
   - Update "Current State" tables if applicable
   - Add to "Change History" sections with date
   - Ensure frontmatter is valid on any new files

4. **Update CHANGELOGs**
   - Project CHANGELOG: If code/feature changes occurred
   - $MAIN_GUIDE Change History: If system config changed
   - Use format: `Date - Title, Changed, Why, Impact`

5. **Confirm reconciliation**
   Report back:
   - What documentation was updated
   - What was intentionally skipped (and why)
   - Any new files created
   - Confirmation that journal can be deleted

### Journal Entry Types → Doc Actions

| Entry Type | Typical Action |
|------------|----------------|
| `## Task Started` | Context only, rarely needs docs |
| `## Discovery` | May need docs if significant finding |
| `## Decision` | Often needs $KNOWLEDGE_BASE/decisions/ or inline update |
| `## Blocker` | May need troubleshooting section update |
| `## Checkpoint` | Context only, rarely needs docs |
| `## Recovery` | May warrant learning doc if significant |
| `## Completed` | Summary guides what needs documentation |

### Example Reconciliation

**Journal excerpt:**
```markdown
### Decision - 14:32
**Context:** Choosing auth strategy for new API
**Content:** Going with JWT over sessions - API is stateless, mobile clients
**Next:** Implement in auth.service.ts

### Completed - 16:45
**Context:** JWT auth implementation done
**Content:** Added JWT middleware, refresh token rotation, 15min access tokens
```

**Reconciliation actions:**
1. ✅ Create `$KNOWLEDGE_BASE/decisions/jwt-auth-strategy.md` (architecture decision)
2. ✅ Update project CHANGELOG (new feature)
3. ⏭️ Skip $MAIN_GUIDE (not system config)
4. ✅ Confirm journal can be deleted

### Invocation

```bash
# After task completion, invoke skill with journal path:
# "Reconcile journal at /tmp/journal-fix-auth-2025-01-15.md"

# Or programmatically in workflow:
# 1. Complete task
# 2. Invoke docs-manager skill
# 3. Provide journal path
# 4. Skill performs reconciliation
# 5. Delete journal after confirmation
```

---

## Worklog Database Integration

**Purpose:** Use shared worklog.db for cross-system knowledge persistence and work tracking.

### Database Location

When `$WORKLOG_DB` is set, the skill integrates with the worklog database.

**Example paths by setup:**
| Setup | Path |
|-------|------|
| Local (default) | `~/.claude/worklog/worklog.db` |
| Shared (network) | `/mnt/share/path/to/worklog.db` |

### When to Store to worklog.db

| Scenario | Store? | Table |
|----------|--------|-------|
| System config change | After documenting | `entries` |
| Reusable knowledge/pattern | Yes | `knowledge_base` |
| Architectural decision | Yes (+ decisions/ doc) | `knowledge_base` |
| Task completion with learnings | Yes | `entries` + `knowledge_base` |
| Incident/issue resolution | Yes | `incidents` |
| Research findings | Yes | `research` |
| Trivial changes | No | - |

### Storing Knowledge

```bash
sqlite3 "$WORKLOG_DB" "INSERT INTO knowledge_base
(category, title, content, tags, source_agent, system) VALUES (
'category-here',
'Title of the Knowledge',
'**Problem:** What was the issue

**Solution:** How to solve it

**Notes:** Gotchas, warnings',
'comma,separated,tags',
'$(hostname)',
'$(hostname)'
);"
```

**Categories:** `learnings`, `guides`, `patterns`, `protocols`, `decisions`

### Logging Work

```bash
sqlite3 "$WORKLOG_DB" "INSERT INTO entries
(agent, task_type, title, details, decision_rationale, outcome, tags, related_files) VALUES (
'$(hostname)',
'documentation',
'Task Title',
'What was done',
'Why this approach',
'Result/outcome',
'docs,tags',
'/path/to/files'
);"
```

### In Journal Reconciliation

**When reconciling journals:**

1. Query worklog.db for related prior context
2. Document outcomes as usual ($MAIN_GUIDE, decisions/, etc.)
3. Store reusable learnings to `knowledge_base` table
4. Log significant work sessions to `entries` table

### Querying Prior Knowledge

```bash
# Search for relevant patterns
sqlite3 "$WORKLOG_DB" \
  "SELECT title, content FROM knowledge_base WHERE tags LIKE '%pattern%';"

# Check recent related work
sqlite3 "$WORKLOG_DB" \
  "SELECT title, outcome FROM entries WHERE tags LIKE '%topic%' ORDER BY timestamp DESC LIMIT 5;"
```

### Working Memory (memories table)

For session-to-session context during tasks:

```bash
# Store working memory
sqlite3 "$WORKLOG_DB" "INSERT INTO memories
(key, content, memory_type, importance, source_agent, system, tags) VALUES (
'mem_' || lower(hex(randomblob(8))),
'[DECISION] Brief title | Details of the decision',
'fact',
7,
'$(hostname)',
'$(hostname)',
'system:shared,type:decision'
);"

# Recall memories
sqlite3 "$WORKLOG_DB" "SELECT key, content FROM memories
WHERE status != 'archived' ORDER BY importance DESC LIMIT 10;"
```

---

## For Future Claude Instances

**Starting a new session?**

1. Read `$DOCS_ROOT/README.md` (navigation)
2. Read relevant section in `$MAIN_GUIDE`
3. Make your changes
4. **UPDATE $MAIN_GUIDE inline** (this is critical!)
5. Use frontmatter on all new docs
6. ALWAYS update CHANGELOG
7. Store reusable learnings to worklog.db (if configured)

**After completing tasks:**
1. Review your journal file
2. Invoke docs-manager for reconciliation
3. Delete journal after confirmation

**Never:**
- Create separate files for incidents/changes
- Leave documentation for "later"
- Add hypothetical content
- Skip frontmatter on new docs
- Delete journal before reconciliation confirms

**Remember:** This system works because it's simple. Keep it simple.

---

**Skill Version:** 2.0.0
**Philosophy:** Single source of truth. Inline updates. Structured knowledge. Queryable metadata. Journal-driven reconciliation. Cross-system worklog.db persistence.
