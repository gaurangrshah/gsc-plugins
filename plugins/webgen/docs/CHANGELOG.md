# Changelog

All notable changes to the WebGen plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.6.0] - 2025-12-17

### Added
- **Git Worktree Integration** - Optional isolated development when existing work detected
  - Automatic detection of uncommitted git work in output directory
  - User opt-in prompt at Checkpoint 1
  - Worktree creation at Architecture phase (`worktrees/{slug}/` on `feat/{slug}` branch)
  - **Mandatory cleanup protocol** - merge to main, delete branches, remove worktree, prune
  - Real-world validation: beacon-advisory-support Astro site conversion
- `skills/worktree-workflow/skill.md` - Setup, working, and cleanup protocols

### Changed
- Checkpoint 1 now detects git repo status and offers worktree option
- Checkpoint 3 (Architecture) creates worktree if user opted in
- Checkpoint 5 (Final) includes mandatory worktree cleanup steps
- README updated with Git Worktree Integration section

## [1.5.0] - 2025-12-13

### Added
- **TaskFlow Integration** - Optional task tracking when TaskFlow plugin is available
  - Detection at Checkpoint 1 with user opt-in
  - Automatic task creation from requirements
  - Status synchronization at each checkpoint
  - Task summary in final report
  - Non-breaking design (WebGen works identically with or without TaskFlow)
- `skills/taskflow-integration/skill.md` - Comprehensive integration guide
- `docs/TASKFLOW-INTEGRATION.md` - User-facing integration documentation
- TaskFlow detection in orchestrator agent

### Changed
- Checkpoint 1 now includes TaskFlow availability detection
- Output template includes TaskFlow opt-in prompt
- README updated with Optional Integrations section
- Plugin structure documentation updated

## [1.4.0] - 2024-12-13

### Added
- **Phase 4.5: Legal Pages** - Conditional phase for generating legal documentation
- Industry-specific legal page templates (Privacy, Terms, Cookies, Disclosures)
- Industry detection table (Fintech, Healthcare, E-commerce, SaaS, General)
- Mandatory legal disclaimer on all generated legal pages
- Footer integration for legal links
- Placeholder markers for business customization (`[COMPANY_NAME]`, `[CONTACT_EMAIL]`)
- GDPR/CCPA compliance baseline in templates
- Industry-specific disclosure sections (SEC for fintech, HIPAA for healthcare)
- **Bundled orchestrator agent** (`webgen-orchestrator.md`) - PM coordination without external dependencies
- **Bundled code reviewer agent** (`webgen-code-reviewer.md`) - Code quality validation included
- **Configurable output directory** (`WEBGEN_OUTPUT_DIR` environment variable)
- **Optional SQLite database** (`WEBGEN_DB_PATH` - empty disables database)
- Comprehensive architecture documentation (`docs/ARCHITECTURE.md`)

### Changed
- Version bumped to 1.4
- Workflow now includes legal page checkpoint between Implementation and Final
- README footer reference updated to v1.4
- Success criteria expanded to include Phase 4.5
- **Plugin is now fully self-contained** - no external agent dependencies
- Output path configurable (default: `./webgen-projects/`)
- Database is now optional (stateless mode when `WEBGEN_DB_PATH` empty)
- Removed hardcoded paths (`/workspace/projects/webgen/` → configurable)

### Removed
- External dependency on shared orchestrator agent
- External dependency on shared code-reviewer agent
- Hardcoded NAS-specific database path

## [1.3.0] - 2024-12-13

### Added
- **Fail-fast infrastructure verification** in Phase 3
- Duplicate project detection before scaffolding
- Network filesystem (SMB/CIFS/NFS) warning and guidance
- Dev server verification before proceeding to code generation
- Hot reload verification during component generation
- Install timeout handling with escalation (no infinite loops)
- `--prefer-offline` flag for faster cached installs
- **Anti-degradation protocol** - prevents quality drop-off toward footer
- Quality checkpoint per section before moving on
- Two-pass generation approach for complex pages
- Reverse-order generation option (footer first, hero last)

### Changed
- Phase 3 renamed to "Architecture + Infrastructure Verification"
- Install + dev server now run BEFORE any code generation
- Phase 4 requires running dev server as prerequisite
- Components verified via hot reload after each generation
- Equal effort mandated for ALL sections (not just hero)
- Version bumped to 1.3

### Fixed
- **Install loop bug** - agent no longer retries indefinitely on failed install
- **Duplicate project creation** - checks for existing project before scaffold
- **Quality degradation** - hero strong but footer weak pattern addressed
- **Monolithic commits** - now enforces atomic commits per section
- **Accessibility gaps** - expanded WCAG checklist with specific requirements

## [1.2.0] - 2024-12-13

### Added
- **Orchestrator integration** - PM oversight at every phase
- 5-checkpoint workflow (Requirements → Research → Architecture → Implementation → Final)
- Phase reporting protocol for orchestrator communication
- Code review integration via orchestrator at Implementation phase
- 2-iteration maximum per phase with escalation to user
- `orchestrated: true` flag in agent frontmatter
- WebGen domain configuration in orchestrator agent

### Changed
- Workflow restructured into discrete phases
- Each phase reports status to orchestrator before proceeding
- Code review now mandatory (dispatched by orchestrator)
- Version bumped to 1.2

## [1.1.0] - 2024-12-13

### Added
- Mandatory TodoWrite integration for progress tracking
- Competitive research capture to `research/competitive-analysis.md`
- Default output location: `/workspace/projects/webgen/`
- Feature branch git workflow with version signatures
- Mandatory testing for API/server projects
- Smart git init (automatic for code, ask for content projects)
- README generation with setup instructions and version footer
- Design decisions documentation (`docs/design-decisions.md`)
- Asset sourcing documentation (`docs/assets.md`)
- Screenshot capture (`docs/screenshots/preview.png`)
- Template promotion workflow
- Agent version tracking
- Accessibility baseline (WCAG 2.1 AA)
- Performance targets (Lighthouse 90+, <200KB bundle)
- 15-point success criteria checklist

### Changed
- Project folder naming includes " - webgen" suffix
- Commits include webgen version in signature

## [1.0.1] - 2024-12-12

### Fixed
- Plugin now properly registered with Claude Code marketplace system
- Created local-plugins marketplace infrastructure (`marketplace.json`)
- Added plugin to `known_marketplaces.json` and `installed_plugins_v2.json`
- Removed stale incomplete plugin directory at `~/.claude/plugins/webgen/`

### Added
- ADR-008: Local Plugin Registration Requirements (documents discovery process and solution)

## [1.0.0] - 2024-12-12

### Added
- Initial release of WebGen Claude Code plugin
- `/webgen` slash command for generating websites from natural language
- `webgen` agent with clarifying questions workflow
- Design system skill with shadcn-inspired patterns
- Project scaffold skill with React+Vite, Astro, and Next.js templates
- Privacy-first approach: never asks for PII, uses placeholder data
- Atomic git workflow with conventional commits
- Support for external design references (URLs, GitHub repos)
