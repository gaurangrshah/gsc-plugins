# Architecture Decision Records

This document records key architectural decisions made for the AppGen plugin.

## ADR-001: 8-Phase Workflow vs 5-Phase (WebGen)

**Status:** Accepted

**Context:**
WebGen uses a 5-phase workflow (Requirements → Research → Architecture → Implementation → Final). AppGen generates more complex applications with databases and APIs.

**Decision:**
Implement an 8-phase workflow:
1. Requirements
2. Research (Tech Stack)
3. Database Design
4. API Design
5. Architecture (Scaffold)
6. Implementation
7. Testing
8. Deployment Config

**Consequences:**
- **Pros:**
  - Database designed before API → APIs designed to match schema
  - API designed before UI → Clear contract, prevents refactoring
  - Testing as explicit phase → Higher test coverage
  - Deployment config → Projects are deployment-ready
- **Cons:**
  - More phases = longer sessions
  - More orchestrator overhead
- **Mitigation:**
  - Phases are focused and move quickly
  - TodoWrite shows clear progress

---

## ADR-002: Database-First Design

**Status:** Accepted

**Context:**
Applications can be designed starting with UI, API, or database. Each approach has trade-offs.

**Decision:**
Design database schema (Phase 3) before API endpoints (Phase 4) or implementation (Phase 6).

**Rationale:**
- Database schema is the foundation
- Changing schema mid-project is costly
- API endpoints should match database entities
- Implementation uses correctly typed entities

**Consequences:**
- **Pros:**
  - Prevents schema refactoring during implementation
  - APIs designed to match data model
  - Type-safe code generation
- **Cons:**
  - Requires clear requirements upfront
  - Hard to change schema later
- **Mitigation:**
  - Thorough requirements gathering (Phase 1)
  - Schema review checkpoint (Orchestrator)

---

## ADR-003: ORM Mandatory, No Raw SQL

**Status:** Accepted

**Context:**
Applications can use ORM (Prisma, Drizzle) or raw SQL queries.

**Decision:**
Always use ORM for database access. Never use raw SQL with string concatenation.

**Rationale:**
- SQL injection is the #1 web vulnerability
- ORMs use parameterized queries by default
- Type-safe queries prevent runtime errors
- Better developer experience

**Consequences:**
- **Pros:**
  - Eliminates SQL injection vulnerabilities
  - Type safety across the stack
  - Automatic migrations
- **Cons:**
  - Some performance overhead
  - Complex queries may be harder
- **Exceptions:**
  - Raw queries allowed only when truly necessary AND parameterized

---

## ADR-004: TypeScript Strict Mode

**Status:** Accepted

**Context:**
TypeScript can be configured with varying strictness levels.

**Decision:**
All generated code uses TypeScript strict mode (`strict: true`, `noImplicitAny: true`, `strictNullChecks: true`).

**Rationale:**
- Catches bugs at compile time
- Forces explicit types, no `any` abuse
- Better IDE support and autocomplete
- Industry best practice

**Consequences:**
- **Pros:**
  - Fewer runtime errors
  - Better refactoring safety
  - Clear contracts between functions
- **Cons:**
  - More verbose code
  - Steeper learning curve
- **Mitigation:**
  - Use type inference where possible
  - Generate well-documented code

---

## ADR-005: Input Validation with Zod

**Status:** Accepted

**Context:**
API inputs can be validated manually, with validation libraries, or with TypeScript alone.

**Decision:**
Use Zod for runtime validation of all API inputs (request body, query params, path params).

**Rationale:**
- TypeScript only validates at compile time, not runtime
- Zod provides runtime type safety
- Zod schemas can be used for TypeScript types
- Clear validation error messages

**Consequences:**
- **Pros:**
  - Runtime type safety
  - Clear validation errors
  - Type inference from schemas
  - Composable validation logic
- **Cons:**
  - Additional dependency
  - Learning curve for Zod syntax
- **Mitigation:**
  - Generate example schemas
  - Document Zod patterns in skills

---

## ADR-006: JWT Authentication Default

**Status:** Accepted

**Context:**
Applications can use session-based auth, JWT, or OAuth.

**Decision:**
Recommend JWT-based authentication for API-only apps, session-based (Auth.js) for Next.js full-stack apps.

**Rationale:**
- **API-only:** JWT is stateless, works well for APIs consumed by SPAs/mobile apps
- **Full-stack:** Session-based (Auth.js) integrates better with Next.js, supports OAuth

**Consequences:**
- **Pros:**
  - Clear guidance for common cases
  - Stateless JWT scales horizontally
  - Auth.js handles OAuth complexity
- **Cons:**
  - JWT token management (refresh tokens)
  - Session storage for full-stack
- **Alternatives:**
  - Lucia for full control
  - Clerk for managed auth

---

## ADR-007: 2-Iteration Maximum

**Status:** Accepted

**Context:**
When orchestrator finds issues, agents can iterate indefinitely or have a maximum.

**Decision:**
Maximum 2 autonomous iterations per phase. After 2 failed iterations, escalate to user.

**Rationale:**
- Prevents infinite loops between agents
- Ensures user oversight on difficult decisions
- Forces agents to focus on critical issues first
- Respects user's time

**Consequences:**
- **Pros:**
  - No infinite loops
  - User can make final decision
  - Agents prioritize critical fixes
- **Cons:**
  - Some phases may need more iterations
- **Mitigation:**
  - User can continue after escalation
  - Agents focus on most important fixes first

---

## ADR-008: Shared Skills with WebGen

**Status:** Accepted

**Context:**
AppGen and WebGen have some overlapping functionality (asset management, TaskFlow integration).

**Decision:**
Copy `asset-management` and `taskflow-integration` skills from WebGen to AppGen.

**Rationale:**
- Consistent asset handling across both plugins
- Consistent TaskFlow integration pattern
- Users familiar with WebGen will understand AppGen

**Consequences:**
- **Pros:**
  - Consistent UX across plugins
  - Less learning curve
  - Asset management works the same
- **Cons:**
  - Duplicate code (two copies of same skill)
  - Updates need to be applied to both
- **Future:**
  - Could create shared plugin for common skills
  - For now, duplication is acceptable

---

## ADR-009: Docker as Deployment Default

**Status:** Accepted

**Context:**
Applications can be deployed via Docker, platform-specific (Vercel), or traditional servers.

**Decision:**
Generate Docker configuration for all projects (Dockerfile + docker-compose.yml).

**Rationale:**
- Docker works across all platforms
- Consistent development/production environment
- Easy local testing
- Platform-agnostic

**Consequences:**
- **Pros:**
  - Works everywhere (local, VPS, cloud)
  - Dev/prod parity
  - Easy to test locally
- **Cons:**
  - Docker learning curve
  - Overhead for simple deployments
- **Alternatives:**
  - Users can deploy to Vercel, Fly.io, etc. without Docker
  - Docker is provided but optional

---

## ADR-010: Testing Infrastructure, Not Full Suite

**Status:** Accepted

**Context:**
AppGen can generate no tests, test infrastructure only, or comprehensive test suites.

**Decision:**
Generate test infrastructure (Vitest, Supertest) and example tests. User writes comprehensive tests.

**Rationale:**
- Test setup is boilerplate and tedious
- Example tests show patterns
- Comprehensive tests depend on business logic
- Can't generate meaningful tests without knowing edge cases

**Consequences:**
- **Pros:**
  - Test infrastructure ready to use
  - Examples show how to test
  - Fast generation (not generating hundreds of tests)
- **Cons:**
  - User still needs to write tests
  - Limited test coverage initially
- **Guidance:**
  - Document testing best practices
  - Example tests for critical paths
  - User extends based on needs

---

## Future ADRs

These decisions may be documented in future versions:

- **GraphQL vs REST:** When to choose GraphQL
- **Monorepo vs Separate Repos:** When to use Turborepo
- **Drizzle vs Prisma:** Trade-offs and recommendations
- **State Management:** Zustand vs Jotai vs Redux
- **Real-time Features:** WebSocket vs SSE vs Polling

---

**Last Updated:** 2024-12-13
**AppGen Version:** 1.0.0
