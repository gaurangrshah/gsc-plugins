# Changelog

All notable changes to the AppGen plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-17

### Added
- **Git Worktree Integration** - Optional isolated development when existing work detected
  - Automatic detection of uncommitted git work in output directory
  - User opt-in prompt at Checkpoint 1
  - Worktree creation at Architecture phase (Checkpoint 5) (`worktrees/{slug}/` on `feat/{slug}` branch)
  - **Mandatory cleanup protocol** - merge to main, delete branches, remove worktree, prune
- `skills/worktree-workflow/skill.md` - Setup, working, and cleanup protocols

### Changed
- Checkpoint 1 now detects git repo status and offers worktree option
- Checkpoint 5 (Architecture) creates worktree if user opted in
- Final Steps include mandatory worktree cleanup steps
- README updated with Git Worktree Integration section

## [1.0.0] - 2024-12-13

### Added

**Core Features:**
- 8-phase orchestrated workflow (Requirements → Research → Database → API → Architecture → Implementation → Testing → Deployment)
- Bundled orchestrator agent for PM coordination
- Bundled code reviewer agent for security and quality validation
- TodoWrite integration for progress tracking
- Optional TaskFlow integration for task tracking
- Git feature branch workflow with atomic commits
- Signed commits with appgen version

**Framework Support:**
- Next.js 15 (App Router) for full-stack apps
- Hono, Express, Fastify for API-only apps
- Turborepo for monorepos

**Database Support:**
- Prisma ORM with schema design patterns
- Drizzle ORM alternative
- PostgreSQL, MySQL, SQLite support
- Migration strategy and seed scripts

**Authentication:**
- Auth.js (NextAuth) for Next.js apps
- Clerk for hosted auth
- Lucia for lightweight custom auth
- JWT-based authentication patterns

**API Design:**
- RESTful endpoint design
- Zod input validation
- Standard error response format
- Pagination patterns

**Testing:**
- Vitest for unit tests
- Supertest for API integration tests
- Playwright for E2E tests (full-stack apps)
- Test database strategies

**Deployment:**
- Docker multi-stage builds
- docker-compose.yml for local development
- .env.example with all variables documented
- README with deployment instructions
- Optional GitHub Actions CI/CD

**Documentation:**
- README.md with setup instructions
- database/schema.md for schema documentation
- api/design.md for API documentation
- docs/architecture.md for architecture overview
- research/tech-stack-analysis.md for tech stack decisions

**Security:**
- Input validation with Zod schemas
- SQL injection prevention via ORM
- XSS prevention
- Authentication and authorization patterns
- Secret management via environment variables
- Security-focused code review

**Skills:**
- `project-scaffold` - Framework setup scripts
- `database-design` - Schema design patterns
- `api-design` - REST API design guidance
- `auth-integration` - Auth provider setup
- `asset-management` - Reference asset cataloging (shared with webgen)
- `taskflow-integration` - Optional task tracking (shared with webgen)

### Configuration

- `APPGEN_OUTPUT_DIR` - Configurable output directory (default: `./appgen-projects`)
- `APPGEN_DB_PATH` - Optional SQLite database for cross-session learning (default: disabled)

### Quality Standards

- TypeScript strict mode enforced
- No `any` types without justification
- JSDoc comments for functions
- Inline comments for complex logic
- Proper error handling with typed errors
- Atomic commits with descriptive messages

### Project Structure

**Next.js Apps:**
- app/ - Next.js App Router structure
- components/ - React components (ui/, features/)
- lib/ - Utilities, database, auth
- prisma/ - Database schema
- tests/ - Unit, integration, E2E tests
- docs/ - Documentation

**API-Only Apps:**
- src/ - Source code (routes/, services/, middleware/, types/)
- prisma/ - Database schema
- tests/ - Unit, integration tests
- docs/ - Documentation

### Success Criteria

A complete appgen session includes:
- All 8 phases completed successfully
- Database schema implemented and documented
- API endpoints implemented and documented
- Authentication integrated (if required)
- Tests passing (unit + integration)
- Docker configuration working
- Documentation complete
- Feature branch merged to main
- Project on main branch

---

## Future Releases

### Planned for v1.1

- GraphQL support with Apollo Server
- More framework options (Remix, SvelteKit)
- MongoDB integration patterns
- Real-time features (WebSocket, SSE)

### Under Consideration

- Deployment platform integrations (Vercel, Fly.io, Railway)
- Monitoring setup (Sentry, LogRocket)
- Email integration (Resend, SendGrid)
- Payment integration (Stripe, Paddle)
- File upload patterns (S3, Cloudflare R2)
- More auth providers (Auth0, Supabase, Firebase)

---

**Legend:**
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Features that will be removed
- **Removed** - Features that were removed
- **Fixed** - Bug fixes
- **Security** - Security improvements
