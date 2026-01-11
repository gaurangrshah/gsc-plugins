# Tech Stack Decision Template

Documentation template for technology selection decisions. Captures rationale for future reference.

## Decision Record

```markdown
# Tech Stack Decision: [Project Name]

**Date:** YYYY-MM-DD
**Decision Maker:** [Agent/User]
**Status:** [Proposed | Accepted | Superseded]

## Context

[Brief description of the project and its requirements]

## Requirements Analysis

### Functional Requirements
- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Non-Functional Requirements
- **Scale:** [Expected users/requests/data volume]
- **Performance:** [Response time, throughput needs]
- **Security:** [Compliance, auth requirements]
- **Budget:** [Infrastructure cost constraints]

## Options Considered

### Option A: [Stack Name]
**Components:** [Framework, DB, etc.]

| Pros | Cons |
|------|------|
| Pro 1 | Con 1 |
| Pro 2 | Con 2 |

**Fit Score:** X/10

### Option B: [Stack Name]
**Components:** [Framework, DB, etc.]

| Pros | Cons |
|------|------|
| Pro 1 | Con 1 |
| Pro 2 | Con 2 |

**Fit Score:** X/10

## Decision

**Selected Stack:** [Option X]

### Rationale
[Detailed explanation of why this option was chosen]

### Trade-offs Accepted
- [Trade-off 1 and mitigation]
- [Trade-off 2 and mitigation]

## Implementation Notes

### Key Dependencies
```json
{
  "framework": "name@version",
  "database": "name@version",
  "orm": "name@version"
}
```

### Configuration Requirements
- [Config item 1]
- [Config item 2]

### Migration Path
[If replacing existing system, describe migration approach]

## Review

**Confidence:** [HIGH | MEDIUM | LOW]
**Review Date:** [When to revisit this decision]
**Triggers for Reconsideration:**
- [Trigger 1]
- [Trigger 2]
```

## Quick Reference Tables

### Framework Selection Matrix

| Requirement | Next.js | Remix | Astro | SvelteKit |
|-------------|---------|-------|-------|-----------|
| SSR/SSG | Both | SSR | SSG-first | Both |
| Data fetching | RSC/API | Loaders | Islands | Load funcs |
| Learning curve | Medium | Medium | Low | Low |
| Enterprise ready | High | High | Medium | Medium |

### Database Selection Matrix

| Requirement | PostgreSQL | SQLite | MongoDB | Redis |
|-------------|------------|--------|---------|-------|
| ACID | Full | Full | Partial | No |
| Scale | High | Low | High | High |
| Complexity | Medium | Low | Low | Low |
| Best for | General | Embedded | Documents | Cache |

### Auth Selection Matrix

| Requirement | Auth.js | Clerk | Lucia | Custom |
|-------------|---------|-------|-------|--------|
| Setup time | Medium | Fast | Medium | Slow |
| Flexibility | High | Low | High | Full |
| Cost | Free | Paid | Free | Varies |
| Maintenance | Medium | Low | Medium | High |

---

**Template Version:** 1.0
**Used By:** appgen (Phase 2), webgen (Phase 2)
**Lines:** ~120
