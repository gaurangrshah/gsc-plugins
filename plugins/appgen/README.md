# AppGen - Claude Code Plugin

Generate full-stack applications and APIs from natural language descriptions using Claude's capabilities directly through your Max subscription.

**Version:** 1.1.0 (Git Worktree Support)

## Overview

AppGen is a **self-contained** Claude Code plugin that transforms natural language descriptions into complete, production-ready full-stack applications and APIs. All agents are bundled—no external dependencies required. It leverages Claude's understanding and code generation capabilities without requiring API costs—just your existing Max subscription.

## Installation

### Option 1: Marketplace (Recommended)

```bash
# Add the marketplace (if not already added)
claude plugin marketplace add https://github.com/gaurangrshah/gsc-plugins.git

# Install the plugin
claude plugin install appgen@gsc-plugins
```

### Option 2: Manual Installation

```bash
# Clone the repo
git clone https://github.com/gaurangrshah/gsc-plugins.git

# Copy to local-plugins
cp -r gsc-plugins/plugins/appgen ~/.claude/plugins/local-plugins/

# Restart Claude Code to activate
```

## Usage

```bash
# With description
/appgen inventory management system for a warehouse

# Interactive mode (asks clarifying questions)
/appgen

# Various project types
/appgen SaaS dashboard for subscription management
/appgen REST API for a blog with auth and comments
/appgen task tracking app with teams and notifications
/appgen e-commerce backend with Stripe integration
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APPGEN_OUTPUT_DIR` | `./appgen-projects` | Base directory for generated applications |
| `APPGEN_DB_PATH` | *(empty)* | SQLite database for cross-session learning (empty = disabled) |

Set these in your environment or shell profile:

```bash
export APPGEN_OUTPUT_DIR="$HOME/my-projects"
export APPGEN_DB_PATH=""  # Leave empty for stateless mode
```

## Standalone & Integration

### Works 100% Standalone

AppGen is fully self-contained. **No other plugins required.**

```bash
# This works perfectly with ONLY appgen installed:
/appgen inventory management system
```

All 8 phases complete. All features work. No errors or warnings about missing plugins.

### Optional Integrations

AppGen detects other GSC plugins and offers enhancements:

#### TaskFlow Integration (Opt-in)

If [TaskFlow](../taskflow/) is installed, AppGen offers task tracking:

```
TaskFlow detected. Track this project with tasks? (y/n)
```

**What happens if you say "yes":**

| Phase | Task Created |
|-------|--------------|
| Requirements | "Define app requirements" |
| Research | "Research tech stack" |
| Database | "Design database schema" |
| API | "Design API endpoints" |
| Architecture | "Define project structure" |
| Implementation | "Implement application" |
| Testing | "Write and run tests" |
| Deployment | "Configure deployment" |

**Benefits:**
- Visual progress tracking through 8 phases
- Clear dependency chains (Database → API → Implementation)
- Resume capability if session interrupted
- Task history for future reference

**What happens if you say "no" or TaskFlow isn't installed:**
- AppGen proceeds with standard workflow
- No errors, no warnings, no prompts
- Identical functionality

#### Git Worktree Integration (Opt-in)

If AppGen detects you have work in progress in the output directory (uncommitted changes in a git repo), it offers isolated development via git worktrees:

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
| Architecture (Phase 5) | Creates worktree at `worktrees/{slug}/` on branch `feat/{slug}` |
| During work | All changes happen in isolated worktree |
| Final | Merges to main, deletes branch, removes worktree, prunes |

**Benefits:**
- Your current work stays untouched
- Parallel development without interference
- Clean merge history
- Automatic cleanup (no orphaned worktrees)

**What happens if you say "no" or no existing work detected:**
- AppGen proceeds with standard feature branch workflow
- No errors, no warnings
- Identical functionality

#### Worklog Integration (Passive)

If [Worklog](../worklog/) is installed, its hooks provide background context:

- **SessionStart hook**: Loads recent work context (if hook_mode is light/full/aggressive)
- **SessionStop hook**: Prompts to store learnings (based on hook_mode setting)

AppGen doesn't actively integrate with Worklog yet, but Worklog's general-purpose hooks still fire during AppGen sessions.

**Future (Planned):**
- Auto-store architecture decisions to knowledge_base
- Query past app scaffolds for patterns
- Track deployment configurations

## Output Location

Projects are created at:
```
{APPGEN_OUTPUT_DIR}/{project-slug} - appgen/
```

**Default:** `./appgen-projects/{project-slug} - appgen/`

This provides a consistent, findable location for all appgen-generated projects.

## How It Works

### Orchestrated Workflow

AppGen uses **@appgen-orchestrator** (bundled) as Product Manager, validating each phase before proceeding:

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
PM reviews tech stack analysis
    ↓
[Checkpoint 3: Database Design]
PM reviews schema and relationships
    ↓
[Checkpoint 4: API Design]
PM reviews endpoints and auth strategy
    ↓
[Checkpoint 5: Architecture Review]
PM reviews structure and tech stack
    ↓
[Checkpoint 6: Code Review]
@appgen-code-reviewer validates implementation
(max 2 iterations, then escalate)
    ↓
[Checkpoint 7: Testing]
PM validates test coverage
    ↓
[Checkpoint 8: Deployment Config]
PM confirms deployment readiness
    ↓
Done
```

### Bundled Agents

| Agent | Purpose |
|-------|---------|
| `@appgen` | Core application generation |
| `@appgen-orchestrator` | PM coordination and quality gates |
| `@appgen-code-reviewer` | Code quality and security validation |

No external agent dependencies required.

**Benefits:**
- Database design reviewed before coding
- API design validated before implementation
- Code review catches security issues early
- 2-iteration max prevents infinite loops
- Escalates to user when agents disagree

### Example Session

```
User: /appgen task tracking app with teams

Agent: [Creates TodoWrite tasks]

First, let me research tech stack options...

[Researches Next.js vs API-only, Prisma vs Drizzle]
[Saves to research/tech-stack-analysis.md]
[Commits: "feat: add tech stack research"]

Now, a few questions:

1. What's the app name?
2. Full-stack (web UI) or API-only?
3. Authentication provider? (Auth.js, Clerk, Lucia)
4. Database? (PostgreSQL, MySQL, SQLite)

User: TaskFlow Pro, full-stack, Auth.js, PostgreSQL

Agent: Creating "TaskFlow Pro" at ./appgen-projects/taskflow-pro - appgen/

Tech stack: Next.js 15 + Prisma + Auth.js
Branch: feat/initial-implementation

[Designs database schema]
[Designs API endpoints]
[Scaffolds Next.js project]
[Generates components with TypeScript]
[Sets up authentication]
[Creates test infrastructure]
[Configures Docker deployment]
[Atomic commits with signature after each phase]

Preview running at http://localhost:3000

Documentation:
- README.md - Setup and deployment instructions
- database/schema.md - Database schema
- api/design.md - API endpoints
- docs/architecture.md - Architecture overview

Generated by appgen v1.0

Next steps:
1. Configure .env with database connection
2. Run database migrations: npm run db:migrate
3. Start development: npm run dev
```

## Key Features

| Feature | Description |
|---------|-------------|
| **8-Phase Workflow** | Requirements → Research → Database → API → Architecture → Implementation → Testing → Deployment |
| **TodoWrite Integration** | Every session tracks progress with todos |
| **TaskFlow Integration** | Optional task tracking when TaskFlow plugin available (non-breaking) |
| **Tech Stack Research** | Saves analysis to `research/` folder |
| **Database-First** | Schema designed before implementation |
| **API-First** | Endpoints designed before UI |
| **Signed Commits** | All commits include `appgen v1.0` signature |
| **Feature Branches** | Uses `feat/{slug}` workflow, atomic commits |
| **Comprehensive Testing** | Unit, integration, and E2E test setup |
| **Security Focus** | Input validation, auth, SQL injection prevention |
| **Deployment Ready** | Docker, CI/CD, environment configuration |
| **Documentation** | README, schema docs, API docs, architecture docs |

## Project Structure

### Next.js Full-Stack App

```
{APPGEN_OUTPUT_DIR}/{project-slug} - appgen/
├── app/
│   ├── (auth)/           # Auth pages (login, signup)
│   ├── (dashboard)/      # Protected dashboard pages
│   ├── api/              # API routes
│   └── layout.tsx        # Root layout
├── components/
│   ├── ui/               # shadcn/ui components
│   └── features/         # Feature components
├── lib/
│   ├── db.ts             # Database client
│   ├── auth.ts           # Auth config
│   └── utils.ts          # Utilities
├── prisma/
│   └── schema.prisma     # Database schema
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── research/
│   └── tech-stack-analysis.md
├── database/
│   └── schema.md         # Schema documentation
├── api/
│   └── design.md         # API documentation
├── docs/
│   └── architecture.md
├── Dockerfile
├── docker-compose.yml
├── CHANGELOG.md
└── README.md
```

### API-Only (Hono)

```
{APPGEN_OUTPUT_DIR}/{project-slug} - appgen/
├── src/
│   ├── routes/           # API route handlers
│   ├── services/         # Business logic
│   ├── middleware/       # Auth, validation
│   ├── types/            # TypeScript types
│   └── index.ts          # App entry
├── prisma/
│   └── schema.prisma
├── tests/
│   ├── unit/
│   └── integration/
├── research/
│   └── tech-stack-analysis.md
├── database/
│   └── schema.md
├── api/
│   └── design.md
├── docs/
│   └── architecture.md
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Tech Stack Options

AppGen supports multiple frameworks and patterns:

### Frameworks

| Type | Options |
|------|---------|
| **Full-Stack** | Next.js 15 (App Router), Remix, SvelteKit |
| **API-Only** | Hono, Express, Fastify |
| **Monorepo** | Turborepo |

### Database & ORM

| ORM | Best For |
|-----|----------|
| **Prisma** | Developer experience, type safety, migrations |
| **Drizzle** | Performance, SQL-like syntax, edge compatibility |

### Authentication

| Provider | Best For |
|----------|----------|
| **Auth.js** | Next.js apps, OAuth providers |
| **Clerk** | Hosted UI, managed auth, quick setup |
| **Lucia** | API-only apps, full control, lightweight |

### Testing

- **Unit:** Vitest
- **Integration:** Supertest (API), Playwright (E2E)
- **Database:** Test containers or SQLite

## Quality Standards

### Security

- **Input Validation:** Zod schemas on all API inputs
- **SQL Injection Prevention:** ORM parameterized queries only
- **XSS Prevention:** No unsafe HTML injection
- **Authentication:** Secure session/token management
- **Authorization:** Resource ownership and RBAC
- **Secrets:** Environment variables, never in code

### Code Quality

- **TypeScript:** Strict mode, no `any` abuse
- **Documentation:** JSDoc for functions, inline comments for complex logic
- **Error Handling:** Try/catch, typed errors, proper HTTP status codes
- **Testing:** Unit tests for services, integration tests for APIs

### Database

- **Schema Types:** Proper types, constraints, defaults
- **Relationships:** Correct foreign keys, cascade rules
- **Indexes:** Foreign keys and frequently queried columns
- **Migrations:** Proper migration files, no manual schema edits

## Plugin Structure

```
appgen/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (v1.0.0)
├── agents/
│   ├── appgen.md                # Core generation agent (v1.0)
│   ├── appgen-orchestrator.md   # PM coordination (bundled)
│   └── appgen-code-reviewer.md  # Code review (bundled)
├── commands/
│   └── appgen.md                # /appgen slash command
├── skills/
│   ├── project-scaffold/
│   │   ├── skill.md
│   │   └── scripts/
│   │       ├── setup-nextjs-app.sh
│   │       ├── setup-api-only.sh
│   │       └── setup-monorepo.sh
│   ├── database-design/
│   │   └── skill.md             # Prisma/Drizzle schema patterns
│   ├── api-design/
│   │   └── skill.md             # REST API design patterns
│   ├── auth-integration/
│   │   └── skill.md             # Auth.js/Clerk/Lucia setup
│   ├── asset-management/
│   │   └── skill.md             # Asset extraction and cataloging
│   └── taskflow-integration/
│       └── skill.md             # Optional TaskFlow task tracking
├── docs/
│   ├── ARCHITECTURE.md          # Full architecture documentation
│   ├── CHANGELOG.md             # Version history
│   └── DECISIONS.md             # Architecture decisions
└── README.md                    # This file
```

**Self-contained:** All required agents and skills bundled. No external dependencies.

## Components

### Command: `/appgen`

Entry point for the plugin. Accepts optional description argument.

```yaml
arguments:
  - name: description
    description: What application to build
    required: false
```

### Agent: `appgen` (v1.0)

The core agent that handles:
- TodoWrite task management (mandatory)
- Tech stack research and analysis
- Intent parsing and clarifying questions
- Database schema design
- API endpoint design
- Project scaffolding with documentation structure
- Code generation with TypeScript strict mode
- Authentication integration
- Feature branch git workflow with signatures
- Testing setup (unit, integration, E2E)
- Deployment configuration (Docker, CI/CD)
- Documentation generation

### Skills

**project-scaffold** - Framework setup scripts (Next.js, Hono, Turborepo)
**database-design** - Prisma/Drizzle schema patterns and best practices
**api-design** - REST API endpoint design with validation and auth
**auth-integration** - Auth.js/Clerk/Lucia setup guides
**asset-management** - Reference asset cataloging (shared with webgen)
**taskflow-integration** - Optional task tracking integration

## Success Criteria

An appgen session is successful when:

- [ ] TodoWrite used throughout the session
- [ ] All 8 checkpoints completed
- [ ] Tech stack research documented
- [ ] Database schema implemented and documented
- [ ] API endpoints designed and documented
- [ ] Git initialized with main branch first
- [ ] Feature branch created for implementation
- [ ] All commits include appgen v1.0 signature
- [ ] Feature branch merged back to main
- [ ] Feature branch deleted after merge
- [ ] Project on main branch (not feature branch)
- [ ] Authentication integrated (if required)
- [ ] Tests passing (unit + integration)
- [ ] Docker configuration working
- [ ] Documentation complete (README, schema, API, architecture)

## History

### v1.0.0 (2024-12-13)

Initial release.

**Features:**
- 8-phase orchestrated workflow
- Database-first design approach
- API-first endpoint design
- Multiple framework support (Next.js, Hono, Turborepo)
- ORM flexibility (Prisma, Drizzle)
- Auth provider options (Auth.js, Clerk, Lucia)
- Comprehensive testing setup
- Docker deployment configuration
- Security-focused code review
- TypeScript strict mode
- Input validation with Zod
- Git feature branch workflow
- Optional TaskFlow integration
- Comprehensive documentation

## Future Considerations

1. **GraphQL Support** - Apollo Server integration for GraphQL APIs
2. **More Frameworks** - Remix, SvelteKit, Astro (server endpoints)
3. **More Databases** - MongoDB, Redis integration patterns
4. **More Auth Providers** - Auth0, Supabase Auth, Firebase Auth
5. **Deployment Platforms** - Vercel, Fly.io, Railway integration
6. **Monitoring Setup** - Sentry, LogRocket integration
7. **Email Integration** - Resend, SendGrid setup
8. **Payment Integration** - Stripe, Paddle patterns
9. **File Upload** - S3, Cloudflare R2 patterns
10. **Real-time Features** - WebSocket, Server-Sent Events

---

🤖 Generated with appgen v1.0
