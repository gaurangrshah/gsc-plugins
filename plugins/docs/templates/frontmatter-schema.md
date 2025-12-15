---
title: "Frontmatter Schema"
type: reference
created: YYYY-MM-DD
---

# Documentation Frontmatter Schema

All markdown documentation must include YAML frontmatter for queryability and organization.

## Required Fields

```yaml
---
title: "Brief descriptive title"
type: decision|learning|guide|reference|changelog|environment
created: YYYY-MM-DD
---
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable document title |
| `type` | enum | Document classification |
| `created` | date | Initial creation date (YYYY-MM-DD) |

### Type Values

| Type | Use Case |
|------|----------|
| `decision` | Architectural or operational decisions |
| `learning` | Lessons learned from incidents or tasks |
| `guide` | How-to documentation and procedures |
| `reference` | Reference documentation and indexes |
| `changelog` | Change history and logs |
| `environment` | Environment-specific documentation |

## Optional Fields

```yaml
updated: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: active|deprecated|superseded
category: "Primary category"
related: [path/to/doc.md]
commit: abc1234
environment: system-name
```

### Optional Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `updated` | date | Last modification date |
| `tags` | array | Keywords for filtering |
| `status` | enum | Document lifecycle state |
| `category` | string | Primary categorization |
| `related` | array | Related document paths |
| `commit` | string | Associated git commit |
| `environment` | string | Target environment |

### Status Values

| Status | Meaning |
|--------|---------|
| `active` | Currently in use |
| `deprecated` | No longer recommended |
| `superseded` | Replaced by newer doc |

## Examples

### Decision Document

```yaml
---
title: "Use JWT for API Authentication"
type: decision
category: security
tags: [auth, api, jwt]
status: active
created: 2025-01-15
---
```

### Learning Document

```yaml
---
title: "CIFS Mount Requires nobrl Option"
type: learning
category: infrastructure
tags: [cifs, mount, sqlite]
created: 2025-01-10
---
```

### Guide Document

```yaml
---
title: "Setting Up SSH Keys"
type: guide
category: security
tags: [ssh, keys, setup]
status: active
created: 2025-01-05
updated: 2025-01-20
---
```

## Validation

Run `docs-validator` to check frontmatter compliance:

```bash
/skill docs-validator --quick
```

Reports:
- Files missing frontmatter
- Invalid field values
- Malformed dates
- Missing required fields
