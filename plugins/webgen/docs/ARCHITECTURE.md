# WebGen Plugin Architecture

**Version:** 1.4.0
**Status:** Self-contained, packagable
**Last Updated:** 2024-12-13

---

## Overview

WebGen is a **self-contained** Claude Code plugin for generating production-ready websites from natural language descriptions. All required agents are bundled—no external dependencies.

---

## Plugin Structure

```
webgen/
├── .claude-plugin/
│   └── plugin.json                 # Plugin manifest (v1.4.0)
│
├── agents/
│   ├── webgen.md                   # Core generation agent (v1.4)
│   ├── webgen-orchestrator.md      # PM coordination agent (bundled)
│   └── webgen-code-reviewer.md     # Code review agent (bundled)
│
├── commands/
│   └── webgen.md                   # /webgen slash command
│
├── skills/
│   ├── design-system/
│   │   ├── skill.md                # CSS tokens, component classes
│   │   └── references/
│   │       └── shadcn.md           # Full component examples
│   │
│   └── project-scaffold/
│       ├── skill.md                # Stack selection guide
│       └── scripts/
│           ├── setup-vite.sh       # React + Vite + Tailwind
│           ├── setup-next.sh       # Next.js + Tailwind
│           └── setup-astro.sh      # Astro + React + Tailwind
│
├── docs/
│   ├── ARCHITECTURE.md             # This file
│   ├── CHANGELOG.md                # Version history
│   ├── DECISIONS.md                # ADRs
│   └── LEARNINGS.md                # Test session insights
│
└── README.md                       # Plugin documentation
```

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WEBGEN PLUGIN (Self-Contained)                      │
│                              Version 1.4.0                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        ENTRY POINT                                   │   │
│  │                                                                       │   │
│  │   /webgen [description]                                              │   │
│  │   └─ commands/webgen.md                                              │   │
│  │      • Invokes @webgen-orchestrator                                  │   │
│  │      • Passes user arguments                                         │   │
│  │      • Documents configuration options                               │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     BUNDLED AGENTS                                   │   │
│  │                                                                       │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                   │   │
│  │  │ webgen-orchestrator │  │ webgen-code-reviewer│                   │   │
│  │  │                     │  │                     │                   │   │
│  │  │ • PM coordination   │  │ • Code quality      │                   │   │
│  │  │ • 5 checkpoints     │  │ • WCAG 2.1 AA       │                   │   │
│  │  │ • 2-iteration max   │  │ • Security review   │                   │   │
│  │  │ • Quality gates     │  │ • Best practices    │                   │   │
│  │  │ • User escalation   │  │ • 2-iteration focus │                   │   │
│  │  └─────────────────────┘  └─────────────────────┘                   │   │
│  │              │                       ▲                               │   │
│  │              │ dispatches            │ reviews                       │   │
│  │              ▼                       │                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                         webgen                               │    │   │
│  │  │                      (Core Agent v1.4)                       │    │   │
│  │  │                                                               │    │   │
│  │  │  Phase 2: Research      │  Phase 3: Architecture             │    │   │
│  │  │  • Competitive analysis │  • Stack selection                 │    │   │
│  │  │  • Industry insights    │  • Project scaffold                │    │   │
│  │  │                         │  • Infrastructure verify           │    │   │
│  │  │  Phase 4: Implementation│  Phase 4.5: Legal Pages            │    │   │
│  │  │  • Section-by-section   │  • Privacy policy                  │    │   │
│  │  │  • Atomic commits       │  • Terms of service                │    │   │
│  │  │  • Anti-degradation     │  • Industry disclosures            │    │   │
│  │  │                         │                                     │    │   │
│  │  │  Phase 5: Final         │                                     │    │   │
│  │  │  • Documentation        │                                     │    │   │
│  │  │  • Screenshot           │                                     │    │   │
│  │  │  • Template promotion   │                                     │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                    │                                 │   │
│  └────────────────────────────────────┼─────────────────────────────────┘   │
│                                       │ references                          │
│                                       ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          SKILLS                                      │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────┐    ┌─────────────────────────┐         │   │
│  │  │ design-system           │    │ project-scaffold        │         │   │
│  │  │                         │    │                         │         │   │
│  │  │ • CSS variables (HSL)   │    │ • setup-vite.sh        │         │   │
│  │  │ • Component classes     │    │ • setup-next.sh        │         │   │
│  │  │ • Responsive patterns   │    │ • setup-astro.sh       │         │   │
│  │  │ • Dark mode support     │    │ • Stack selection      │         │   │
│  │  │ • shadcn.md reference   │    │ • Folder structures    │         │   │
│  │  └─────────────────────────┘    └─────────────────────────┘         │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ Runtime Requirements
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RUNTIME ENVIRONMENT                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Claude Code     │  │ Node.js 18+     │  │ Git 2.30+       │             │
│  │                 │  │                 │  │                 │             │
│  │ • TodoWrite     │  │ • pnpm (8+)     │  │ • git init      │             │
│  │ • WebFetch      │  │ • npm/yarn alt  │  │ • git commit    │             │
│  │ • Bash          │  │ • vite/next cli │  │ • git push      │             │
│  │ • Write/Edit    │  │ • astro cli     │  │                 │             │
│  │ • Task (agents) │  │                 │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ OPTIONAL: SQLite Database                                            │   │
│  │                                                                       │   │
│  │ If WEBGEN_DB_PATH is set:                                            │   │
│  │ • Cross-session learning                                             │   │
│  │ • Industry-specific pattern storage                                  │   │
│  │ • Preference persistence                                             │   │
│  │                                                                       │   │
│  │ If empty/unset: Stateless mode (no database required)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `WEBGEN_OUTPUT_DIR` | `./webgen-projects` | No | Base directory for generated projects |
| `WEBGEN_DB_PATH` | *(empty)* | No | SQLite database for cross-session learning |

### Output Path Resolution

```
1. Check WEBGEN_OUTPUT_DIR environment variable
2. If unset, use ./webgen-projects relative to cwd
3. Create directory if it doesn't exist
4. Project created at: {output_dir}/{project-slug} - webgen/
```

### Database Behavior

```
If WEBGEN_DB_PATH is set:
  → Query for prior context on session start
  → Store learnings on session end
  → Industry-specific patterns accumulate

If WEBGEN_DB_PATH is empty:
  → Skip all database operations
  → Fully stateless operation
  → No cross-session memory
```

---

## Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INVOCATION                                │
│                                                                             │
│   /webgen restaurant landing page for Bistro Bliss                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT 1: REQUIREMENTS                           @webgen-orchestrator  │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Parse user request                                                        │
│ • Gather: project type, industry, design preferences, audience             │
│ • Confirm with user before proceeding                                      │
│ • Determine output directory                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT 2: RESEARCH                               @webgen → orchestrator │
├─────────────────────────────────────────────────────────────────────────────┤
│ • @webgen conducts competitive research (2-3 competitors)                  │
│ • Saves to research/competitive-analysis.md                                │
│ • Orchestrator reviews: competitors appropriate? insights actionable?      │
│ • Max 2 iterations if issues found                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT 3: ARCHITECTURE                           @webgen → orchestrator │
├─────────────────────────────────────────────────────────────────────────────┤
│ • @webgen scaffolds project with selected stack                            │
│ • Runs pnpm install (fail-fast verification)                               │
│ • Starts dev server and verifies                                           │
│ • Orchestrator reviews: stack appropriate? infrastructure working?         │
│ • BLOCKS if infrastructure fails                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT 4: IMPLEMENTATION                @webgen → @webgen-code-reviewer │
├─────────────────────────────────────────────────────────────────────────────┤
│ • @webgen generates components section-by-section                          │
│ • Anti-degradation protocol (equal effort per section)                     │
│ • Atomic commits after each section                                        │
│ • @webgen-code-reviewer validates: quality, a11y, security                 │
│ • Max 2 iterations if issues found                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT 4.5: LEGAL PAGES (Conditional)                          @webgen │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Triggered if: data collection, auth, payments, regulated industry        │
│ • Skipped if: simple portfolio, docs, internal tools                       │
│ • Generates: Privacy Policy, Terms, industry-specific disclosures          │
│ • Includes mandatory legal disclaimer on all pages                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT 5: FINAL                                  @webgen → orchestrator │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Generate README.md with version footer                                   │
│ • Generate docs/design-decisions.md                                        │
│ • Generate docs/assets.md                                                  │
│ • Capture screenshot to docs/screenshots/preview.png                       │
│ • Orchestrator confirms all requirements met                               │
│ • Offer template promotion                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PROJECT COMPLETE                                │
│                                                                             │
│  Output: {WEBGEN_OUTPUT_DIR}/{slug} - webgen/                              │
│  Preview: http://localhost:5173 (Vite) | :3000 (Next) | :4321 (Astro)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## File Inventory

### Total: 16 files

| Path | Type | Purpose | ~Size |
|------|------|---------|-------|
| `.claude-plugin/plugin.json` | Manifest | Plugin registration | 1KB |
| `agents/webgen.md` | Agent | Core generation (v1.4) | 25KB |
| `agents/webgen-orchestrator.md` | Agent | PM coordination | 12KB |
| `agents/webgen-code-reviewer.md` | Agent | Code review | 8KB |
| `commands/webgen.md` | Command | Entry point | 4KB |
| `skills/design-system/skill.md` | Skill | CSS tokens, classes | 10KB |
| `skills/design-system/references/shadcn.md` | Reference | Component examples | 15KB |
| `skills/project-scaffold/skill.md` | Skill | Stack guide | 5KB |
| `skills/project-scaffold/scripts/setup-vite.sh` | Script | Vite scaffold | 6KB |
| `skills/project-scaffold/scripts/setup-next.sh` | Script | Next.js scaffold | 5KB |
| `skills/project-scaffold/scripts/setup-astro.sh` | Script | Astro scaffold | 5KB |
| `docs/ARCHITECTURE.md` | Doc | This file | 12KB |
| `docs/CHANGELOG.md` | Doc | Version history | 4KB |
| `docs/DECISIONS.md` | Doc | ADRs | 2KB |
| `docs/LEARNINGS.md` | Doc | Test insights | 5KB |
| `README.md` | Doc | Plugin docs | 15KB |

**Estimated Total: ~130KB**

---

## External Dependencies

### None Required

This plugin is **fully self-contained**. All agents are bundled:

| Agent | Location | Purpose |
|-------|----------|---------|
| `@webgen` | `agents/webgen.md` | Core website generation |
| `@webgen-orchestrator` | `agents/webgen-orchestrator.md` | PM coordination |
| `@webgen-code-reviewer` | `agents/webgen-code-reviewer.md` | Code quality validation |

### Runtime Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Claude Code | Latest | Agent runtime, tools |
| Node.js | 18+ | JavaScript runtime |
| pnpm | 8+ | Package manager (preferred) |
| Git | 2.30+ | Version control |

### Optional

| Requirement | Purpose |
|-------------|---------|
| SQLite | Cross-session learning (if WEBGEN_DB_PATH set) |

---

## Packaging Checklist

To distribute this plugin:

```bash
# Create distribution package
cd ~/.claude/plugins/local-plugins/
zip -r webgen-v1.4.0.zip webgen/ \
  -x "webgen/.git/*" \
  -x "webgen/node_modules/*"

# Or tar
tar -czvf webgen-v1.4.0.tar.gz webgen/ \
  --exclude='.git' \
  --exclude='node_modules'
```

### Pre-distribution Checklist

- [x] All agents bundled (webgen, webgen-orchestrator, webgen-code-reviewer)
- [x] No external agent dependencies
- [x] Hardcoded paths replaced with configurable variables
- [x] Database dependency made optional
- [x] plugin.json version updated to 1.4.0
- [x] README documents configuration options
- [x] CHANGELOG updated with packaging changes
- [ ] Test on fresh system (pending)

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0.0 | 2024-12-12 | Initial release |
| 1.1.0 | 2024-12-13 | Research capture, signed commits |
| 1.2.0 | 2024-12-13 | External orchestrator integration |
| 1.3.0 | 2024-12-13 | Fail-fast, anti-degradation |
| 1.4.0 | 2024-12-13 | **Self-contained packaging** |

### v1.4.0 Packaging Changes

- Bundled `webgen-orchestrator` agent (was external)
- Bundled `webgen-code-reviewer` agent (was external)
- Made output directory configurable (`WEBGEN_OUTPUT_DIR`)
- Made database optional (`WEBGEN_DB_PATH`, empty = disabled)
- Removed all hardcoded paths
- No external dependencies required
