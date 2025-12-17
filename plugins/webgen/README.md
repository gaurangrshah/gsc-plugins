# WebGen - Claude Code Plugin

Generate websites, components, and features from natural language descriptions using Claude's capabilities directly through your Max subscription.

**Version:** 1.6.0 (Git Worktree Support)

## Overview

WebGen is a **self-contained** Claude Code plugin that transforms natural language descriptions into complete, production-ready web projects. All agents are bundled—no external dependencies required. It leverages Claude's understanding and code generation capabilities without requiring API costs—just your existing Max subscription.

## Installation

The plugin is already installed at:
```
~/.claude/plugins/local-plugins/webgen/
```

Restart Claude Code to activate it.

## Usage

```bash
# With description
/webgen restaurant landing page for Bistro Bliss

# Interactive mode (asks clarifying questions)
/webgen

# Various project types
/webgen portfolio site for a freelance photographer
/webgen pricing component with 3 tiers
/webgen SaaS dashboard with analytics widgets
/webgen multi-page healthcare site for Clarity Health
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBGEN_OUTPUT_DIR` | `./webgen-projects` | Base directory for generated projects |
| `WEBGEN_DB_PATH` | *(empty)* | SQLite database for cross-session learning (empty = disabled) |

Set these in your environment or shell profile:

```bash
export WEBGEN_OUTPUT_DIR="$HOME/my-projects"
export WEBGEN_DB_PATH=""  # Leave empty for stateless mode
```

## Standalone & Integration

### Works 100% Standalone

WebGen is fully self-contained. **No other plugins required.**

```bash
# This works perfectly with ONLY webgen installed:
/webgen restaurant landing page
```

All 5 checkpoints complete. All features work. No errors or warnings about missing plugins.

### Optional Integrations

WebGen detects other GSC plugins and offers enhancements:

#### TaskFlow Integration (Opt-in)

If [TaskFlow](../taskflow/) is installed, WebGen offers task tracking:

```
TaskFlow detected. Track this project with tasks? (y/n)
```

**What happens if you say "yes":**

| Checkpoint | Task Created |
|------------|--------------|
| Requirements | "Define project requirements" |
| Research | "Conduct competitive research" |
| Architecture | "Design project architecture" |
| Implementation | "Implement components" |
| Final Sign-off | "Complete documentation" |

**Benefits:**
- Visual progress tracking during generation
- Clear dependency chains (Research → Architecture → Implementation)
- Resume capability if session interrupted
- Task history for future reference

**What happens if you say "no" or TaskFlow isn't installed:**
- WebGen proceeds with standard workflow
- No errors, no warnings, no prompts
- Identical functionality

#### Git Worktree Integration (Opt-in)

If WebGen detects you have work in progress in the output directory (uncommitted changes in a git repo), it offers isolated development via git worktrees:

```
**Git Worktree (Recommended):**
I detected you have work in progress in the output directory.
Would you like to use a git worktree?

- **Yes** - Create isolated worktree (keeps your current work untouched)
- **No** - Use standard feature branch in output directory
```

**What happens if you say "yes":**

| Phase | Action |
|-------|--------|
| Architecture | Creates worktree at `worktrees/{slug}/` on branch `feat/{slug}` |
| During work | All changes happen in isolated worktree |
| Final | Merges to main, deletes branch, removes worktree, prunes |

**Benefits:**
- Your current work stays untouched
- Parallel development without interference
- Clean merge history
- Automatic cleanup (no orphaned worktrees)

**Real-world example:** Successfully used for beacon-advisory-support project - full Astro site conversion in isolated worktree, cleanly merged to main.

**What happens if you say "no" or no existing work detected:**
- WebGen proceeds with standard feature branch workflow
- No errors, no warnings
- Identical functionality

#### Worklog Integration (Passive)

If [Worklog](../worklog/) is installed, its hooks provide background context:

- **SessionStart hook**: Loads recent work context (if hook_mode is light/full/aggressive)
- **SessionStop hook**: Prompts to store learnings (based on hook_mode setting)

WebGen doesn't actively integrate with Worklog yet, but Worklog's general-purpose hooks still fire during WebGen sessions.

**Future (Planned):**
- Auto-store design patterns to knowledge_base
- Query similar past projects for consistency
- Track generation metrics

## Output Location

Projects are created at:
```
{WEBGEN_OUTPUT_DIR}/{project-slug} - webgen/
```

**Default:** `./webgen-projects/{project-slug} - webgen/`

This provides a consistent, findable location for all webgen-generated projects.

## How It Works

### Orchestrated Workflow (v1.4)

WebGen uses **@webgen-orchestrator** (bundled) as Product Manager, validating each phase before proceeding:

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
(max 2 iterations, then escalate)
    ↓
[Checkpoint 4.5: Legal Pages]
(Conditional - if applicable)
    ↓
[Checkpoint 5: Final Sign-off]
PM confirms all requirements met
    ↓
Done
```

### Bundled Agents

| Agent | Purpose |
|-------|---------|
| `@webgen` | Core website generation |
| `@webgen-orchestrator` | PM coordination and quality gates |
| `@webgen-code-reviewer` | Code quality and accessibility validation |

No external agent dependencies required.

**Benefits:**
- Research reviewed before wasting time on wrong direction
- Architecture approved before coding begins
- Code review catches issues early
- 2-iteration max prevents infinite loops
- Escalates to user when agents disagree

### Example Session

```
User: /webgen fintech landing page

Agent: [Creates TodoWrite tasks]

First, let me research competitors...

[Researches Betterment, Wealthfront, Oscar Health]
[Saves to research/competitive-analysis.md]
[Commits: "feat: add competitive research"]

Now, a few questions:

1. What's the company/product name?
2. Key sections needed? (Based on research: Hero, Features, Trust indicators, Pricing, CTA)
3. Design preference? (Competitors use clean, trustworthy designs)

User: InvestWise, modern minimal, all those sections

Agent: Creating "InvestWise" at ./webgen-projects/investwise - webgen/

Tech stack: React + Vite + Tailwind
Branch: feat/initial-scaffold

[Scaffolds project with research/, docs/ folders]
[Generates components with docstrings]
[Atomic commits with signature after each feature]
[Captures screenshot]
[Generates README, design-decisions.md, assets.md]

Preview running at http://localhost:5173

Research saved in research/competitive-analysis.md
Design decisions documented in docs/design-decisions.md

Generated by webgen v1.4

Should this become a reusable template?
```

## Key Features (v1.5)

| Feature | Description |
|---------|-------------|
| **Asset Management** | Detects, catalogs, and propagates reference assets (screenshots, designs) throughout workflow |
| **TodoWrite Integration** | Every session tracks progress with todos |
| **TaskFlow Integration** | Optional task tracking when TaskFlow plugin available (non-breaking) |
| **Competitive Research** | Saves competitor analysis to `research/` folder |
| **Signed Commits** | All commits include `webgen v1.4` signature |
| **Feature Branches** | Uses `feat/{slug}` workflow, atomic commits |
| **Documentation** | Generates README, design-decisions, assets docs |
| **Screenshot Capture** | Saves preview to `docs/screenshots/preview.png` |
| **Legal Pages** | Industry-specific privacy, terms, disclosures |
| **Template Promotion** | Successful projects can become reusable templates |
| **Testing** | Mandatory test suite for API/server projects |
| **Accessibility** | WCAG 2.1 AA compliance baseline |
| **Performance Targets** | Lighthouse 90+, <200KB bundle documented |

## Project Structure

### Code Projects

```
{WEBGEN_OUTPUT_DIR}/{project-slug} - webgen/
├── .webgen/                      # WebGen metadata
│   └── assets/                   # Reference assets catalog
│       ├── catalog.json          # Asset metadata and manifest
│       ├── screenshots/          # UI reference screenshots
│       ├── designs/              # Design files
│       └── references/           # Other reference materials
├── research/
│   └── competitive-analysis.md   # Competitor insights
├── docs/
│   ├── design-decisions.md       # Colors, fonts, spacing, breakpoints
│   ├── assets.md                 # Asset sources and attribution
│   └── screenshots/
│       └── preview.png           # Final preview screenshot
├── src/
│   └── components/               # Generated components with docstrings
├── tests/                        # For API/server projects (MANDATORY)
├── CHANGELOG.md
├── README.md                     # Includes "Generated by webgen v1.4"
└── package.json
```

### Content Projects (emails, brochures, campaigns)

```
{project-slug} - webgen/
├── research/                     # If git approved
│   └── competitive-analysis.md
├── content/
└── README.md
```

### Templates Location

```
{WEBGEN_OUTPUT_DIR}/templates/{category}/
```

## Asset Management (v1.5)

**NEW:** WebGen now detects and catalogs reference assets (screenshots, designs) provided in the initial prompt, making them available throughout the entire workflow.

### How It Works

1. **Provide Assets:** Attach screenshots, design files, or reference images when invoking `/webgen`
2. **Automatic Detection:** Orchestrator detects files and dispatches @webgen for extraction
3. **Cataloging:** Assets are cataloged in `.webgen/assets/catalog.json` with metadata
4. **Propagation:** Every phase receives asset context in dispatch prompts
5. **Implementation:** Implementation agents read assets before coding for pixel-perfect results

### Example Workflow

```
User: /webgen restaurant landing page
[Attaches: hero-reference.png, features-grid.png]

Orchestrator:
- Detects 2 assets
- Dispatches @webgen for extraction
- Creates .webgen/assets/catalog.json
- Includes asset context in all phase dispatches

Research Phase:
- @webgen reads assets to understand visual style
- Finds competitors with similar layouts

Architecture Phase:
- @webgen analyzes screenshots to identify needed components
- Plans Hero, Features Grid components

Implementation Phase:
- @webgen reads hero-reference.png
- Extracts colors, spacing, layout
- Implements pixel-perfect Hero component matching reference
- Documents asset usage in component docstrings
```

### Asset Types Supported

| Type | Examples | Detection |
|------|----------|-----------|
| **Screenshots** | UI mockups, reference pages | .png, .jpg, .jpeg attachments |
| **Designs** | Figma/Sketch exports | .fig, .sketch, .pdf exports |
| **References** | Brand guidelines, wireframes | .pdf, image files |

### Asset Catalog Schema

```json
{
  "version": "1.0",
  "assets": [
    {
      "id": "asset-1",
      "type": "screenshot",
      "path": ".webgen/assets/screenshots/hero-reference.png",
      "description": "Hero section with gradient background",
      "usedIn": ["architecture", "implementation"],
      "tags": ["hero", "layout", "gradient"]
    }
  ]
}
```

### Benefits

- **Pixel-perfect implementation** - Components match provided references
- **Faster iteration** - No guessing about desired design
- **Better communication** - Visual references clearer than text descriptions
- **Documented decisions** - Asset usage documented in component docstrings

## Design Decisions

### Why a Claude Code Plugin?

**Background:** This started as a standalone Next.js app using local LLMs (Ollama with Llama 3.1 and CodeLlama). After extensive experimentation, we pivoted to a claude code plugin (we were already paying for the subscription).

### Privacy-First Approach

**Problem:** Generating websites often requires contact information, but had industry specific considerations:
Don't want to: 
- Ask users for personal information
- Store PII in prompts or outputs
- Risk exposing real contact details

**Solution:** The agent NEVER asks for PII. For contact sections, it generates believable placeholders:
- **Address:** "123 Main Street, Anytown, ST 12345"
- **Phone:** "555-XXX-XXXX" (reserved for fiction by telecom standards)
- **Email:** "contact@{business-slug}.example.com"
- **Social:** Uses "#" as placeholder URLs

The user adds real data locally after generation. Possible future consideration for a --pii-safe flag and allow the normal Q&A to get company details if they exist.

### Tech Stack Selection

| Scenario | Stack | Reason |
|----------|-------|--------|
| Simple landing page | React + Vite | Fast, simple, no SSR complexity |
| Portfolio, marketing | React + Vite | Static content, quick dev |
| Blog, documentation | Astro | Content-focused, partial hydration |
| App with API routes | Next.js | Server-side features needed |
| E-commerce, auth | Next.js | Dynamic content, SSR/SSG |

Default: **React + Vite + Tailwind** for most landing pages.

### Git Workflow (v1.4)

**Feature Branch Workflow:**
1. **Initialize with main branch FIRST** (Phase 3):
   ```bash
   git init
   git add .gitignore README.md package.json  # Minimum viable files
   git commit -m "chore: initial project structure"
   git branch -M main  # Ensure on main branch
   ```
2. **Create feature branch for implementation:**
   ```bash
   git checkout -b feat/initial-implementation
   ```
3. **Atomic commits** after each logical unit with signature:
   ```
   feat: add hero section

   🤖 Generated with webgen v1.4
   Agent: webgen v1.4
   ```
4. **Push regularly:** `git push -u origin HEAD`
5. **Merge back to main before completion** (Phase 5):
   ```bash
   git checkout main
   git merge feat/initial-implementation --no-ff -m "feat: complete {project-name}"
   git branch -d feat/initial-implementation  # Clean up
   ```
6. **Final state:** Project on `main` branch with feature branch deleted

**CRITICAL:** Project MUST end on `main` branch with all changes merged.

**Content Projects:** Git is optional - agent asks before initializing.

### Asset Sourcing

Default placeholder sources:
- **Photos:** Unsplash (free, high-quality)
- **Dimensions:** placeholder.com
- **Icons:** Heroicons, Lucide
- **Illustrations:** unDraw

All sources documented in `docs/assets.md` with attribution requirements.

## Quality Standards

### Accessibility (WCAG 2.1 AA)

All generated code must include:
- Semantic HTML (`nav`, `main`, `section`, `article`)
- Proper heading hierarchy (h1 → h2 → h3)
- Alt text for all images
- Focus states for interactive elements
- Color contrast 4.5:1 minimum

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Lighthouse Performance | 90+ | For production builds |
| Lighthouse Accessibility | 100 | WCAG 2.1 AA compliance |
| Lighthouse Best Practices | 90+ | Modern web standards |
| Bundle Size | < 200KB | Initial load, simple sites |
| First Contentful Paint | < 1.5s | User perception |
| Time to Interactive | < 3.5s | Usability threshold |

Targets are documented in generated README.

### Code Documentation

All generated code includes:
- Module-level docstrings (purpose, design decisions)
- Function-level docstrings (what, parameters, returns)
- Inline comments for complex logic (WHY, not WHAT)
- Placeholder: `// TODO: Integrate with marketing reference library when available`

## Plugin Structure

```
webgen/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (v1.5.0)
├── agents/
│   ├── webgen.md                # Core generation agent (v1.5)
│   ├── webgen-orchestrator.md   # PM coordination (bundled)
│   └── webgen-code-reviewer.md  # Code review (bundled)
├── commands/
│   └── webgen.md                # /webgen slash command
├── skills/
│   ├── asset-management/
│   │   └── skill.md             # Asset extraction, catalog, propagation
│   ├── design-system/
│   │   ├── skill.md             # Color tokens, component classes
│   │   └── references/
│   │       └── shadcn.md        # Full component examples
│   ├── project-scaffold/
│   │   ├── skill.md             # Stack selection guide
│   │   └── scripts/
│   │       ├── setup-vite.sh    # React + Vite + Tailwind
│   │       ├── setup-next.sh    # Next.js + Tailwind
│   │       └── setup-astro.sh   # Astro + React + Tailwind
│   └── taskflow-integration/
│       └── skill.md             # Optional TaskFlow task tracking
├── docs/
│   ├── ARCHITECTURE.md          # Full architecture documentation
│   ├── CHANGELOG.md             # Version history
│   ├── DECISIONS.md             # Architecture decisions
│   └── LEARNINGS.md             # Test session insights
└── README.md                    # This file
```

**Self-contained:** All required agents and skills bundled. No external dependencies.

## Components

### Command: `/webgen`

Entry point for the plugin. Accepts optional description argument.

```yaml
arguments:
  - name: description
    description: What to generate
    required: false
```

### Agent: `webgen` (v1.4)

The core agent that handles:
- TodoWrite task management (mandatory)
- Competitive research and capture
- Intent parsing and clarifying questions
- Stack selection
- Project scaffolding with documentation structure
- Code generation with docstrings
- Feature branch git workflow with signatures
- Testing setup for APIs/servers
- Screenshot capture
- Documentation generation
- Template promotion

### Skill: `design-system`

Provides:
- **Color tokens** - Primary (indigo), secondary (gray), accent (amber)
- **Component classes** - btn, card, nav, hero, section, cta, footer
- **Responsive patterns** - Container, grids, typography scale
- **Dark mode** - Automatic via `.dark` class

### Skill: `project-scaffold`

Provides:
- **Stack templates** - React+Vite, Astro, Next.js
- **Common files** - globals.css, tailwind.config.js
- **Folder structures** - Recommended organization per stack
- **Quick start** - CLI commands for each stack

## Success Criteria

A webgen session is successful when:

- [ ] TodoWrite used throughout the session
- [ ] **Assets extracted and cataloged** (if provided)
- [ ] **Asset catalog created** at `.webgen/assets/catalog.json` (if assets provided)
- [ ] **Assets read in implementation phase** (if provided)
- [ ] Competitive research saved (when applicable)
- [ ] Project created at `{WEBGEN_OUTPUT_DIR}/{slug} - webgen/`
- [ ] Git initialized with main branch first
- [ ] Feature branch created for implementation
- [ ] All commits include webgen v1.4 signature
- [ ] Feature branch merged back to main
- [ ] Feature branch deleted after merge
- [ ] Project on main branch (not feature branch)
- [ ] Code includes proper documentation
- [ ] **Asset usage documented in component docstrings** (if applicable)
- [ ] Tests included for API/server projects
- [ ] Accessibility baseline met (WCAG 2.1 AA)
- [ ] Performance targets documented
- [ ] README.md complete with version footer
- [ ] Design decisions documented
- [ ] Asset sources documented
- [ ] Preview screenshot captured
- [ ] Template promotion asked
- [ ] Research persisted, not ephemeral

## History

### v1.5.0 (2024-12-13)

**Asset Management System.**

**Added:**
- **Asset extraction and cataloging** in Phase 1 (Requirements)
- **Asset-management skill** for extraction, catalog, and propagation
- **Asset context propagation** through all workflow phases
- Asset awareness in Research phase (inform research direction)
- Asset awareness in Architecture phase (identify components)
- **Mandatory asset reading** in Implementation phase (pixel-perfect matching)
- Asset catalog schema with metadata (id, type, path, description, usedIn, tags)
- `.webgen/assets/` directory structure (screenshots, designs, references)
- Updated orchestrator to include asset context in all phase dispatches
- Documentation of asset workflow in README

**Changed:**
- Phase 1 renamed: "Requirements" → "Requirements + Asset Extraction"
- Implementation phase now requires reading reference assets before coding
- Component docstrings must document asset usage when applicable

**Benefits:**
- Pixel-perfect implementations matching user-provided references
- Faster iterations with visual references
- Better communication via screenshots vs text descriptions

### v1.4.0 (2024-12-13)

**Self-Contained Packaging + Legal Pages.**

**Added:**
- Phase 4.5: Legal Pages (conditional phase)
- Industry-specific templates (Privacy, Terms, Cookies, Disclosures)
- Mandatory legal disclaimer on all generated legal pages
- **Bundled orchestrator agent** (`webgen-orchestrator.md`)
- **Bundled code reviewer agent** (`webgen-code-reviewer.md`)
- **Configurable output directory** (`WEBGEN_OUTPUT_DIR`)
- **Optional SQLite database** (`WEBGEN_DB_PATH`, empty = disabled)
- Comprehensive architecture documentation

**Changed:**
- Workflow includes legal checkpoint between Implementation and Final
- **Plugin is now fully self-contained** - no external agent dependencies
- Output path configurable (default: `./webgen-projects/`)
- Database is now optional (stateless mode when empty)
- Removed all hardcoded paths

### v1.3 (2024-12-13)

**Fail-fast infrastructure + Quality assurance.**

**Added:**
- Fail-fast infrastructure verification (install + dev server before coding)
- Anti-degradation protocol (equal effort per section)
- Section-by-section atomic commits
- Expanded accessibility checklist (WCAG 2.1 AA per component)
- Network filesystem warning
- Install timeout with escalation

**Fixed:**
- Install loop bug (no more infinite retries)
- Duplicate project creation (existence check)
- Quality degradation (hero strong, footer weak)
- Monolithic commits (now atomic per section)

### v1.2 (2024-12-13)

**Orchestrated workflow - PM oversight at every phase.**

**Added:**
- Orchestrator integration as Product Manager
- 5-checkpoint workflow (Requirements → Research → Architecture → Implementation → Final)
- Phase reporting protocol for orchestrator communication
- Code review integration at Implementation phase
- 2-iteration maximum per phase with escalation
- Orchestrated: true flag in agent frontmatter

**Changed:**
- Version bumped to 1.2
- Workflow restructured into discrete phases
- Each phase reports status to orchestrator
- Code review now mandatory (via orchestrator)

### v1.1 (2024-12-13)

Major update adding comprehensive documentation, research capture, and quality standards.

**Added:**
- Mandatory TodoWrite integration for progress tracking
- Competitive research capture to `research/competitive-analysis.md`
- Default output location: `/workspace/projects/webgen/`
- Feature branch git workflow with version signatures
- Mandatory testing for API/server projects
- Smart git init (auto for code, ask for content projects)
- README generation with setup instructions and version footer
- Design decisions documentation (`docs/design-decisions.md`)
- Asset sourcing documentation (`docs/assets.md`)
- Screenshot capture (`docs/screenshots/preview.png`)
- Template promotion workflow
- Agent version tracking (v1.1)
- Accessibility baseline (WCAG 2.1 AA)
- Performance targets (Lighthouse 90+, <200KB bundle)
- 15-point success criteria checklist

**Changed:**
- Project folder naming includes " - webgen" suffix
- Commits include webgen version in signature

### v1.0.1 (2024-12-12)

**Fixed:**
- Plugin now properly registered with Claude Code marketplace system
- Created local-plugins marketplace infrastructure

### v1.0.0 (2024-12-12)

Initial release after pivoting from local LLM experiment.

**What we learned from the Ollama experiment:**
- Local LLMs aren't reliable enough for structured output
- Code completion models (CodeLlama) copy examples verbatim
- Orchestration (LangChain) doesn't fix model capability issues
- Claude's instruction-following is the real differentiator

**Archived:** The original Next.js + Ollama experiment is preserved at:
- Repo: `/home/gs/projects/experiments/webgen`
- Branch: `archive/local-llm-experiment`

## Future Considerations

1. **Marketing reference library** - Centralized patterns for marketing projects
2. **Template expansion** - More starter templates (blog, e-commerce, dashboard)
3. **Design presets** - Industry-specific color schemes
4. **Component library** - Pre-built complex components
5. **Integration hooks** - Post-generation hooks for deployment setup
