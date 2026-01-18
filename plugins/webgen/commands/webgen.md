---
description: Generate websites, components, or features from natural language
arguments:
  - name: description
    description: What to generate (e.g., "restaurant landing page", "pricing component")
    required: false
---

# WebGen Command

Generate web projects from natural language descriptions with orchestrated quality control.

## Usage

```
/webgen [description]
```

## Examples

```
/webgen restaurant landing page for Bistro Bliss
/webgen portfolio site for a freelance designer
/webgen pricing component with 3 tiers
/webgen multi-page healthcare site for Clarity Health
/webgen                  # Interactive mode - will ask questions
```

## Configuration

### Output Directory

Projects are created in a configurable location:

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBGEN_OUTPUT_DIR` | `./webgen-projects` | Base directory for generated projects |

Set via environment variable or the orchestrator will use the default.

### Database (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBGEN_DB_PATH` | *(empty)* | SQLite for cross-session learning. Empty = disabled |

---

## Orchestrated Workflow

WebGen uses **@webgen-orchestrator** as Product Manager to ensure quality at every phase:

```
User Request
    ↓
┌─────────────────────────────────────┐
│   @webgen-orchestrator (PM Agent)   │
│  Validates requirements, approves   │
│  each phase, manages iterations     │
└─────────────────────────────────────┘
    ↓
[Checkpoint 1: Requirements]
PM validates scope and requirements
    ↓
[Checkpoint 2: Research Review]
PM reviews competitive analysis
    ↓
[Checkpoint 3: Architecture Review]
PM reviews structure and tech stack
    ↓
[Checkpoint 4: Code Review]
@webgen-code-reviewer validates implementation
    ↓
[Checkpoint 4.5: Legal Pages]
(Conditional - if applicable)
    ↓
[Checkpoint 5: Final Sign-off]
PM confirms all requirements met
    ↓
Done
```

## Key Features

- **PM Orchestration:** Every phase reviewed before proceeding
- **Quality Gates:** 2-iteration max per phase, then escalates to user
- **Configurable Output:** Projects go to `{WEBGEN_OUTPUT_DIR}/{slug} - webgen/`
- **Competitive Research:** Saves competitor analysis to `research/` folder
- **Comprehensive Documentation:** README, design decisions, asset sources
- **Screenshot Capture:** Saves preview to docs/screenshots/preview.png
- **Default Design System:** GSDEV Baseline 2026 with OKLch colors - see KB 451
- **Accessibility Baseline:** WCAG 2.1 AA compliance
- **Performance Targets:** Documents Lighthouse and bundle size goals
- **Legal Pages:** Industry-specific privacy, terms, disclosures with disclaimers
- **Signed Work:** All commits include webgen v1.5 signature
- **Feature Branches:** Uses git feature branch workflow
- **Testing:** Automatic test setup for API/server projects
- **Template Promotion:** Offers to save successful projects as reusable templates

## Bundled Agents

This plugin includes all required agents:

| Agent | Purpose |
|-------|---------|
| `@webgen` | Core website generation agent |
| `@webgen-orchestrator` | PM coordination and quality gates |
| `@webgen-code-reviewer` | Code quality and accessibility validation |

No external agent dependencies required.

## Invoke Orchestrator

This command invokes the **@webgen-orchestrator** agent to manage the workflow.

The orchestrator will:
1. Validate requirements with user (Checkpoint 1)
2. Dispatch @webgen for research phase, then review (Checkpoint 2)
3. Dispatch @webgen for scaffold phase, then review (Checkpoint 3)
4. Dispatch @webgen for code generation, dispatch @webgen-code-reviewer (Checkpoint 4)
5. Dispatch @webgen for legal pages if applicable (Checkpoint 4.5)
6. Final sign-off confirming all requirements met (Checkpoint 5)

**Orchestration Context:**

```
Domain: webgen
Creator Agent: @webgen
Reviewer Agent: @webgen-code-reviewer
Orchestrator: @webgen-orchestrator
Phases: requirements → research → architecture → implementation → legal → final
Output: ${WEBGEN_OUTPUT_DIR:-./webgen-projects}/{project-slug} - webgen/
Preferences: ${WEBGEN_OUTPUT_DIR:-./webgen-projects}/preferences.md (optional)
Database: ${WEBGEN_DB_PATH} (optional, empty = disabled)
Max Iterations: 2 per phase (then escalate to user)
```

$ARGUMENTS
