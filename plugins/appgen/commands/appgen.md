---
description: Generate full-stack applications and APIs from natural language
arguments:
  - name: description
    description: What application to build (e.g., "inventory management system", "REST API for a blog")
    required: false
---

# AppGen Command

Generate full-stack applications and APIs from natural language descriptions with orchestrated quality control.

## Usage

```
/appgen [description]
```

## Examples

```
/appgen inventory management system for a warehouse
/appgen REST API for a blog with auth and comments
/appgen SaaS dashboard for subscription management
/appgen task tracking app with teams and notifications
/appgen e-commerce backend with Stripe integration
/appgen                  # Interactive mode - will ask questions
```

## Configuration

### Output Directory

Projects are created in a configurable location:

| Variable | Default | Description |
|----------|---------|-------------|
| `APPGEN_OUTPUT_DIR` | `~/projects/appgen` | Base directory for generated applications |

Set via environment variable or the orchestrator will use the default.

### Database (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `APPGEN_DB_PATH` | *(empty)* | SQLite for cross-session learning. Empty = disabled |

---

## Orchestrated Workflow

AppGen uses **@appgen-orchestrator** as Product Manager to ensure quality at every phase:

```
User Request
    ↓
┌─────────────────────────────────────┐
│  @appgen-orchestrator (PM Agent)    │
│  Validates requirements, approves   │
│  each phase, manages iterations     │
└─────────────────────────────────────┘
    ↓
[Checkpoint 1: Requirements]
PM validates scope and requirements
    ↓
[Checkpoint 2: Research Review]
PM reviews tech stack decisions
    ↓
[Checkpoint 3: Database Design]
PM reviews schema and relationships
    ↓
[Checkpoint 4: API Design]
PM reviews endpoints and auth strategy
    ↓
[Checkpoint 5: Architecture Review]
PM reviews component structure
    ↓
[Checkpoint 6: Implementation]
@appgen-code-reviewer validates code
    ↓
[Checkpoint 7: Testing]
PM validates test coverage
    ↓
[Checkpoint 8: Deployment Config]
PM confirms deployment readiness
    ↓
Done
```

## Key Features

- **PM Orchestration:** Every phase reviewed before proceeding
- **Quality Gates:** 2-iteration max per phase, then escalates to user
- **Database-First:** Schema design before implementation
- **API-First:** Endpoint design before UI
- **Configurable Output:** Projects go to `{APPGEN_OUTPUT_DIR}/{slug} - appgen/`
- **Tech Stack Research:** Analysis of framework and library options
- **Comprehensive Testing:** Unit, integration, and E2E test setup
- **Authentication:** Auth.js/Clerk/Lucia integration options
- **Database:** SQLite with adapter pattern (upgradeable to Postgres) - see KB 449
- **Deployment Config:** Docker, CI/CD, environment setup
- **Signed Work:** All commits include appgen v1.1 signature
- **Feature Branches:** Uses git feature branch workflow

## Bundled Agents

This plugin includes all required agents:

| Agent | Purpose |
|-------|---------|
| `@appgen` | Core application generation agent |
| `@appgen-orchestrator` | PM coordination and quality gates |
| `@appgen-code-reviewer` | Code quality and testing validation |

No external agent dependencies required.

## Invoke Orchestrator

This command invokes the **@appgen-orchestrator** agent to manage the workflow.

The orchestrator will:
1. Validate requirements with user (Checkpoint 1)
2. Dispatch @appgen for research phase, then review (Checkpoint 2)
3. Dispatch @appgen for database design, then review (Checkpoint 3)
4. Dispatch @appgen for API design, then review (Checkpoint 4)
5. Dispatch @appgen for architecture, then review (Checkpoint 5)
6. Dispatch @appgen for implementation, dispatch @appgen-code-reviewer (Checkpoint 6)
7. Dispatch @appgen for testing setup, then review (Checkpoint 7)
8. Dispatch @appgen for deployment config, then review (Checkpoint 8)

**Orchestration Context:**

```
Domain: appgen
Creator Agent: @appgen
Reviewer Agent: @appgen-code-reviewer
Orchestrator: @appgen-orchestrator
Phases: requirements → research → database → api → architecture → implementation → testing → deployment
Output: ${APPGEN_OUTPUT_DIR:-~/projects/appgen}/{project-slug} - appgen/
Preferences: ${APPGEN_OUTPUT_DIR:-~/projects/appgen}/preferences.md (optional)
Database: ${APPGEN_DB_PATH} (optional, empty = disabled)
Max Iterations: 2 per phase (then escalate to user)
```

$ARGUMENTS
