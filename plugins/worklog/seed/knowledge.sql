-- Worklog Seed Data: Bootstrap Knowledge Entries
-- Essential documentation to help users get started

-- Quick Start Guide
INSERT INTO knowledge_base (category, title, content, tags, source_agent) VALUES
('protocols', 'Worklog Quick Start Guide',
'# Worklog Quick Start

Cross-session knowledge persistence for AI agents.

## Core Tools

| Tool | Purpose |
|------|---------|
| `recall_context(topic)` | Load relevant context before starting tasks |
| `search_knowledge(query)` | Full-text search the knowledge base |
| `store_knowledge(...)` | Save reusable documentation |
| `store_memory(...)` | Save session context, facts, preferences |
| `log_entry(...)` | Log work completed |

## Workflow

**At task start:**
```
recall_context(topic="relevant-topic")
```

**During work:**
- Store important decisions as memories
- Log significant progress

**At task end:**
```
store_knowledge(...) # If learnings are reusable
log_entry(...)       # Record what was done
```

## Categories

Use these canonical categories for `store_knowledge`:

| Category | Use For |
|----------|---------|
| `infrastructure` | Servers, Docker, networking, deployment |
| `development` | Code patterns, tooling, workflows |
| `protocols` | Mandatory procedures, guardrails |
| `decisions` | Architecture/design decisions (ADRs) |
| `projects` | Project-specific context |

## Tips

- Query context before unfamiliar tasks
- Store learnings after completing significant work
- Use consistent tags for discoverability
- Keep entries focused and actionable
', 'worklog,quickstart,onboarding,getting-started', 'worklog-init')
ON CONFLICT (category, title) DO NOTHING;

-- Schema Reference
INSERT INTO knowledge_base (category, title, content, tags, source_agent) VALUES
('protocols', 'Worklog Schema Reference',
'# Worklog Schema Reference

Which data belongs in which table.

## Tables

| Table | Purpose | Example Content |
|-------|---------|-----------------|
| `knowledge_base` | Reusable documentation | Guides, decisions, patterns |
| `memories` | Session context, facts | Task tracking, preferences |
| `entries` | Work log records | Task completions, daily logs |
| `research` | Analysis artifacts | Tool evaluations, article summaries |
| `known_issues` | Documented problems | Gotchas with workarounds |

## Decision Tree

```
What am I storing?
│
├─ Reusable documentation/guide? → knowledge_base
├─ Session context/task tracking? → memories
├─ Work completion record? → entries
├─ Tool evaluation/analysis? → research
└─ Known problem with workaround? → known_issues
```

## Memory Types

| Type | Use For |
|------|---------|
| `fact` | Learnings, decisions, knowledge |
| `context` | Task tracking, in-progress work |
| `preference` | User preferences |
| `entity` | Project/system metadata |

## Importance Levels

| Level | Meaning |
|-------|---------|
| 1-4 | Low value, may be pruned |
| 5-6 | Standard context |
| 7-8 | Valuable, promote to KB |
| 9-10 | Critical, always retain |
', 'worklog,schema,reference,tables', 'worklog-init')
ON CONFLICT (category, title) DO NOTHING;

-- Tag Usage Guide
INSERT INTO knowledge_base (category, title, content, tags, source_agent) VALUES
('protocols', 'Worklog Tagging Guide',
'# Worklog Tagging Guide

Consistent tagging improves discoverability.

## Tag Normalization

Tags are automatically normalized to canonical forms:

| You Write | Stored As |
|-----------|-----------|
| k8s, kube | kubernetes |
| postgres, pg | postgresql |
| auth, authn | authentication |
| ssl, tls, https | ssl-tls |

## Best Practices

1. **Use lowercase** - Tags are case-insensitive
2. **Use hyphens** - `ssl-tls` not `ssl_tls`
3. **Be specific** - `react-hooks` not just `react`
4. **Limit count** - 3-5 tags per entry is ideal

## Common Tags by Category

**Infrastructure:** docker, kubernetes, postgresql, traefik, networking
**Development:** typescript, react, testing, api, debugging
**Security:** authentication, ssl-tls, secrets, permissions
**Operations:** monitoring, backup, logging, deployment
', 'worklog,tags,tagging,conventions', 'worklog-init')
ON CONFLICT (category, title) DO NOTHING;
