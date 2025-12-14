# AppGen Architecture

**Version:** 1.0.0
**Last Updated:** 2024-12-13

## Overview

AppGen is a Claude Code plugin for generating full-stack applications and APIs from natural language descriptions. It follows an 8-phase orchestrated workflow with quality gates at each checkpoint.

## Core Components

### 1. Command Layer

**`/appgen` command** - Entry point for the plugin

```
User invokes: /appgen inventory management system
    ↓
Command dispatches @appgen-orchestrator
    ↓
Orchestrator manages workflow through 8 checkpoints
```

### 2. Agent Layer

Three bundled agents work together:

**@appgen** - Core generation agent
- Handles each phase of generation
- Reports to orchestrator after each phase
- Makes targeted fixes based on feedback
- Maximum 2 iterations per phase

**@appgen-orchestrator** - Product Manager
- Validates requirements with user
- Dispatches @appgen for each phase
- Reviews deliverables at each checkpoint
- Dispatches @appgen-code-reviewer for code validation
- Escalates to user after 2 failed iterations

**@appgen-code-reviewer** - Code reviewer
- Reviews generated code for quality, security, type safety
- Focuses on critical issues first
- Provides actionable feedback
- Maximum 2 rounds of review

### 3. Skill Layer

Six skills provide specialized knowledge:

| Skill | Purpose |
|-------|---------|
| `project-scaffold` | Framework setup scripts (Next.js, Hono, Turborepo) |
| `database-design` | Schema design patterns (Prisma, Drizzle) |
| `api-design` | REST API design, validation, auth |
| `auth-integration` | Auth.js, Clerk, Lucia setup |
| `asset-management` | Reference asset cataloging |
| `taskflow-integration` | Optional task tracking |

## Workflow Architecture

### 8-Phase Checkpoint System

```
┌─────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                      │
│              (Product Manager Agent)                │
└─────────────────────────────────────────────────────┘
    │
    ├─[Checkpoint 1: Requirements]────────────────────┐
    │  - Gather app type, features, auth, database    │
    │  - Get user confirmation                        │
    │  - Dispatch @appgen with confirmed requirements │
    └─────────────────────────────────────────────────┘
    │
    ├─[Checkpoint 2: Research]────────────────────────┐
    │  - @appgen researches tech stack options        │
    │  - Saves to research/tech-stack-analysis.md     │
    │  - Orchestrator reviews recommendations         │
    │  - Max 2 iterations if issues found             │
    └─────────────────────────────────────────────────┘
    │
    ├─[Checkpoint 3: Database Design]─────────────────┐
    │  - @appgen designs schema (Prisma/Drizzle)      │
    │  - Saves to database/schema.md + schema file    │
    │  - Orchestrator reviews entities/relationships  │
    │  - Max 2 iterations if issues found             │
    └─────────────────────────────────────────────────┘
    │
    ├─[Checkpoint 4: API Design]──────────────────────┐
    │  - @appgen designs endpoints, auth, validation  │
    │  - Saves to api/design.md                       │
    │  - Orchestrator reviews RESTful design          │
    │  - Max 2 iterations if issues found             │
    └─────────────────────────────────────────────────┘
    │
    ├─[Checkpoint 5: Architecture]────────────────────┐
    │  - @appgen scaffolds project structure          │
    │  - Installs dependencies, configures tools      │
    │  - Verifies infrastructure (npm install, dev)   │
    │  - Orchestrator reviews before coding           │
    └─────────────────────────────────────────────────┘
    │
    ├─[Checkpoint 6: Implementation]──────────────────┐
    │  - @appgen generates application code           │
    │  - Atomic commits per feature                   │
    │  - @appgen-code-reviewer validates code         │
    │  - Orchestrator coordinates feedback loop       │
    │  - Max 2 iterations total                       │
    └─────────────────────────────────────────────────┘
    │
    ├─[Checkpoint 7: Testing]─────────────────────────┐
    │  - @appgen sets up test infrastructure          │
    │  - Generates example tests (unit, integration)  │
    │  - Orchestrator verifies tests pass             │
    │  - Max 2 iterations if issues found             │
    └─────────────────────────────────────────────────┘
    │
    └─[Checkpoint 8: Deployment Config]───────────────┐
       - @appgen creates Docker configuration         │
       - Creates .env.example with all variables      │
       - Updates README with deployment instructions  │
       - Orchestrator confirms deployment readiness   │
       └─────────────────────────────────────────────┘
```

## Key Architectural Decisions

### 1. Database-First Approach

**Decision:** Design database schema before API endpoints or implementation.

**Rationale:**
- Database schema is the foundation of the application
- Prevents refactoring due to schema changes
- API endpoints can be designed to match schema
- Implementation can use correctly typed entities

**Trade-offs:**
- Requires clear understanding of requirements upfront
- Schema changes mid-project are costly
- Mitigation: Thorough requirements gathering in Phase 1

### 2. API-First Approach

**Decision:** Design API endpoints before frontend implementation.

**Rationale:**
- Clear contract between frontend and backend
- Enables parallel frontend/backend development
- Input validation schemas defined upfront
- Security considerations addressed early

**Trade-offs:**
- API may need changes based on UI needs
- Mitigation: Include UI flows in requirements, design APIs to support them

### 3. 2-Iteration Maximum

**Decision:** Maximum 2 autonomous iterations per phase, then escalate to user.

**Rationale:**
- Prevents infinite loops between agents
- Ensures user oversight on difficult decisions
- Forces agents to focus on critical issues first
- Respects user's time

**Trade-offs:**
- Some phases may need more iterations
- Mitigation: User can continue after escalation, agents focus on most important fixes

### 4. TypeScript Strict Mode

**Decision:** All generated code uses TypeScript strict mode.

**Rationale:**
- Catches bugs at compile time
- Better IDE support and autocomplete
- Forces explicit types, no `any` abuse
- Industry best practice for production apps

**Trade-offs:**
- Slightly more verbose code
- Learning curve for beginners
- Mitigation: Generate well-documented code, use type inference where possible

### 5. ORM Over Raw SQL

**Decision:** Use ORM (Prisma or Drizzle) for database access, never raw SQL.

**Rationale:**
- Prevents SQL injection vulnerabilities
- Type-safe queries
- Automatic migrations
- Better developer experience

**Trade-offs:**
- Some performance overhead
- Complex queries may be harder
- Mitigation: Use raw queries only when truly necessary, still parameterized

## Security Architecture

### Defense in Depth

1. **Input Layer** - Zod validation on all API inputs
2. **Application Layer** - Authentication and authorization checks
3. **Database Layer** - ORM parameterized queries, no raw SQL
4. **Transport Layer** - HTTPS enforced, secure cookies
5. **Secrets Layer** - Environment variables, no hardcoded secrets

### Authentication Flow

```
User Login Request
    ↓
[Zod validation]
    ↓
[Lookup user by email]
    ↓
[Verify password with bcrypt]
    ↓
[Create session/JWT]
    ↓
[Set secure cookie or return token]
    ↓
Success Response
```

### Authorization Patterns

**Resource Ownership:**
```typescript
// User can only access their own data
const userId = c.get('userId');  // From auth middleware
const post = await prisma.post.findUnique({ where: { id: postId } });

if (post.authorId !== userId) {
  return c.json({ error: 'Forbidden' }, 403);
}
```

**Role-Based Access:**
```typescript
// Admin-only endpoints
const user = await prisma.user.findUnique({ where: { id: userId } });

if (user.role !== 'ADMIN') {
  return c.json({ error: 'Admin required' }, 403);
}
```

## Testing Architecture

### Test Pyramid

```
          ┌───────┐
         /  E2E   \       # Few comprehensive flows
        /───────────\
       /Integration \     # API endpoints with database
      /───────────────\
     /      Unit      \   # Services, utilities, validation
    /─────────────────\
```

**Unit Tests (Most):**
- Business logic in services
- Utility functions
- Validation schemas
- Fast, isolated, no database

**Integration Tests (Some):**
- API endpoints with test database
- Database operations
- Authentication flows
- Slower, use test containers or SQLite

**E2E Tests (Few):**
- Critical user flows
- Full-stack tests (if applicable)
- Slowest, most fragile, highest value

## Git Workflow

### Feature Branch Strategy

```
main (protected)
  └─feat/initial-implementation
      ├─commit: "feat: add database schema"
      ├─commit: "feat: add API endpoints"
      ├─commit: "feat: add authentication"
      ├─commit: "feat: add tests"
      └─commit: "feat: add deployment config"
  └─merge to main
  └─delete feature branch
```

**Benefits:**
- Clean main branch
- Atomic commits with clear history
- Easy to review changes
- Easy to revert if needed

## Error Handling

### Error Categories

| Category | HTTP Status | Example |
|----------|-------------|---------|
| Validation | 400 | Invalid email format |
| Auth | 401 | Missing token |
| Authorization | 403 | Not your resource |
| Not Found | 404 | User doesn't exist |
| Conflict | 409 | Email already in use |
| Business Logic | 422 | Can't delete published post |
| Server Error | 500 | Database connection failed |

### Error Response Format

```typescript
{
  error: {
    code: "VALIDATION_ERROR",
    message: "Invalid request body",
    details: [
      { field: "email", message: "Invalid email format" }
    ]
  }
}
```

## Configuration Management

### Environment Variables

All configuration via environment variables:

```env
# Database
DATABASE_URL="postgresql://..."

# Auth
NEXTAUTH_SECRET="..."
JWT_SECRET="..."

# App
NODE_ENV="development"
PORT=3000

# External Services (if needed)
STRIPE_SECRET_KEY="..."
SENDGRID_API_KEY="..."
```

### Configuration Layers

1. `.env.example` - Template with all variables (committed)
2. `.env` - Local values (gitignored)
3. `docker-compose.yml` - Development defaults
4. Production platform - Vercel/Fly.io/Railway variables

## Deployment Architecture

### Docker Multi-Stage Build

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
```

**Benefits:**
- Smaller production image
- Build dependencies not in production
- Faster deployments

### Docker Compose

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/myapp
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Future Architecture Considerations

### Scalability

- **Horizontal Scaling:** Stateless design allows multiple app instances
- **Database Connection Pooling:** Prevent connection exhaustion
- **Caching:** Redis for session storage and frequently accessed data
- **CDN:** Cloudflare/Vercel for static assets

### Monitoring

- **Application Monitoring:** Sentry for error tracking
- **Performance Monitoring:** New Relic or DataDog
- **Logging:** Structured logs to CloudWatch or Logtail
- **Uptime Monitoring:** Pingdom or UptimeRobot

### CI/CD

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

---

**Last Updated:** 2024-12-13
**AppGen Version:** 1.0.0
