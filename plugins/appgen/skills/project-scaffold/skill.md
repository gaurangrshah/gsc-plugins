---
title: Project Scaffold Skill
type: skill
created: 2024-12-13
tags: [appgen, scaffold, nextjs, api, setup]
---

# Project Scaffold Skill

Provides setup scripts and guidance for scaffolding full-stack applications and APIs.

## Purpose

This skill helps the appgen agent scaffold projects using the appropriate framework and structure based on the application type.

## Application Types

### 1. Full-Stack App (Next.js)

**Use when:** Building complete web applications with frontend and backend.

**Framework:** Next.js 15 (App Router)

**Features:**
- Server and Client Components
- Built-in API routes
- TypeScript
- Tailwind CSS
- Automatic code splitting

**Script:** `./scripts/setup-nextjs-app.sh`

**Usage:**
```bash
./setup-nextjs-app.sh "project-name" "/output/path"
```

### 2. API-Only

**Use when:** Building backend services, REST APIs, GraphQL servers.

**Framework Options:**
- **Hono** - Ultrafast, edge-ready (recommended)
- **Express** - Traditional, mature ecosystem
- **Fastify** - High performance, schema validation

**Features:**
- TypeScript
- Minimal dependencies
- Fast startup
- Easy to containerize

**Script:** `./scripts/setup-api-only.sh`

**Usage:**
```bash
./setup-api-only.sh "project-name" "/output/path" "hono|express|fastify"
```

### 3. Monorepo (Turborepo)

**Use when:** Multiple apps/packages need to share code.

**Framework:** Turborepo

**Structure:**
```
monorepo/
├── apps/
│   ├── web/          # Next.js app
│   └── api/          # Hono API
├── packages/
│   ├── database/     # Prisma schema + client
│   ├── ui/           # Shared UI components
│   └── typescript-config/  # Shared tsconfig
└── turbo.json
```

**Script:** `./scripts/setup-monorepo.sh`

**Usage:**
```bash
./setup-monorepo.sh "project-name" "/output/path"
```

---

## Decision Matrix

| Requirement | Recommended Type |
|-------------|------------------|
| SaaS dashboard with UI | Full-Stack (Next.js) |
| Admin panel | Full-Stack (Next.js) |
| REST API for mobile app | API-Only (Hono) |
| GraphQL server | API-Only (Express + Apollo) |
| Microservices | API-Only (Hono or Fastify) |
| Multiple frontends sharing API | Monorepo |
| Mobile + Web sharing backend | Monorepo |

---

## Common Dependencies

### Database & ORM

**Prisma:**
```bash
npm install prisma @prisma/client
npm install -D prisma
```

**Drizzle:**
```bash
npm install drizzle-orm
npm install -D drizzle-kit
```

### Validation

**Zod:**
```bash
npm install zod
```

### Authentication

**Auth.js (Next.js):**
```bash
npm install next-auth
```

**Lucia (Universal):**
```bash
npm install lucia @lucia-auth/adapter-prisma
```

### Testing

**Vitest:**
```bash
npm install -D vitest @vitest/ui
```

**Supertest (API testing):**
```bash
npm install -D supertest @types/supertest
```

**Playwright (E2E):**
```bash
npm install -D @playwright/test
```

---

## Project Structure Conventions

### Next.js App Router

```
project-name/
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
│   └── schema.prisma
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/
```

### API-Only (Hono)

```
project-name/
├── src/
│   ├── routes/           # API route handlers
│   │   ├── users.ts
│   │   └── posts.ts
│   ├── services/         # Business logic
│   ├── middleware/       # Auth, validation
│   ├── types/            # TypeScript types
│   └── index.ts          # App entry
├── prisma/
│   └── schema.prisma
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
```

### Monorepo

```
monorepo/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # Hono backend
├── packages/
│   ├── database/         # Shared Prisma
│   ├── ui/               # Shared components
│   ├── typescript-config/
│   └── eslint-config/
├── turbo.json
└── package.json
```

---

## Configuration Files

### TypeScript (tsconfig.json)

**Strict mode:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### ESLint (.eslintrc.json)

```json
{
  "extends": ["next/core-web-vitals", "prettier"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

### Prettier (.prettierrc)

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

---

## Setup Script Requirements

All setup scripts must:
1. Create project directory
2. Initialize package.json
3. Install dependencies
4. Configure TypeScript (strict mode)
5. Configure ESLint
6. Configure Prettier
7. Create .gitignore
8. Create folder structure
9. Create README.md with setup instructions

---

## Usage Examples

### Example 1: Next.js SaaS App

```bash
# Scaffold Next.js app
cd /path/to/appgen-projects
./setup-nextjs-app.sh "task-manager" "."

# Result:
# - task-manager - appgen/
# - Next.js 15 with App Router
# - TypeScript configured
# - Tailwind CSS
# - Ready for database integration
```

### Example 2: Hono API

```bash
# Scaffold Hono API
cd /path/to/appgen-projects
./setup-api-only.sh "blog-api" "." "hono"

# Result:
# - blog-api - appgen/
# - Hono framework
# - TypeScript configured
# - Basic route structure
# - Ready for Prisma integration
```

### Example 3: Turborepo Monorepo

```bash
# Scaffold monorepo
cd /path/to/appgen-projects
./setup-monorepo.sh "acme" "."

# Result:
# - acme - appgen/
# - Turborepo structure
# - web app (Next.js)
# - api app (Hono)
# - Shared packages
```

---

## Post-Scaffold Steps

After running a scaffold script, the appgen agent should:

1. **Verify infrastructure:**
   ```bash
   cd project-dir
   npm install  # Should succeed
   npm run dev  # Should start (if applicable)
   ```

2. **Add database:**
   - Initialize Prisma or Drizzle
   - Create schema.prisma
   - Configure database connection

3. **Add authentication:**
   - Use auth-integration skill
   - Install auth provider
   - Configure middleware

4. **Document architecture:**
   - Create docs/architecture.md
   - Document tech stack choices
   - Document folder structure

---

## Troubleshooting

### npm install fails

**Symptoms:**
- Network errors
- Permission errors
- Conflicting dependencies

**Solutions:**
1. Check internet connection
2. Clear npm cache: `npm cache clean --force`
3. Try with --legacy-peer-deps flag
4. Check Node.js version (>=18.0.0)

### Dev server won't start

**Symptoms:**
- Port already in use
- Missing dependencies
- Configuration errors

**Solutions:**
1. Kill process on port: `lsof -ti:3000 | xargs kill`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Check for syntax errors in config files

---

## Version History

**v1.0** (2024-12-13)
- Initial skill for appgen plugin
- Setup scripts for Next.js, API-only, Monorepo
- Project structure conventions
- Configuration examples
