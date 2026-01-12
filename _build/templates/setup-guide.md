# Setup Guide Template

Documentation template for project setup and development environment instructions.

## Project Setup Guide

```markdown
# [Project Name] - Setup Guide

## Prerequisites

### Required
- Node.js >= 20.x (recommend using mise or nvm)
- pnpm >= 9.x (or npm/yarn)
- Git >= 2.x

### Optional
- Docker & Docker Compose (for database/services)
- [Database] if not using Docker

## Quick Start

### 1. Clone Repository
```bash
git clone [repository-url]
cd [project-name]
```

### 2. Install Dependencies
```bash
pnpm install
```

### 3. Environment Setup
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
# Database
DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"

# Auth
AUTH_SECRET="generate-with-openssl-rand-base64-32"

# Optional services
REDIS_URL="redis://localhost:6379"
```

### 4. Database Setup
```bash
# Start database (if using Docker)
docker compose up -d db

# Run migrations
pnpm db:migrate

# Seed data (optional)
pnpm db:seed
```

### 5. Start Development Server
```bash
pnpm dev
```

Open http://localhost:3000

## Project Structure

```
[project-name]/
├── src/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   │   ├── ui/          # Base UI components
│   │   └── features/    # Feature components
│   ├── lib/             # Utilities & helpers
│   ├── server/          # Server-side code
│   │   ├── api/         # API routes
│   │   └── db/          # Database layer
│   └── types/           # TypeScript types
├── prisma/              # Database schema
├── public/              # Static assets
├── tests/               # Test files
└── docs/                # Documentation
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Build for production |
| `pnpm start` | Start production server |
| `pnpm lint` | Run ESLint |
| `pnpm test` | Run tests |
| `pnpm db:migrate` | Run database migrations |
| `pnpm db:studio` | Open Prisma Studio |

## Development Workflow

### Creating a Feature
1. Create feature branch: `git checkout -b feat/feature-name`
2. Implement changes
3. Write/update tests
4. Run lint and tests: `pnpm lint && pnpm test`
5. Commit with conventional commit: `git commit -m "feat: add feature"`
6. Push and create PR

### Database Changes
1. Edit `prisma/schema.prisma`
2. Generate migration: `pnpm prisma migrate dev --name description`
3. Update seed data if needed
4. Commit migration files

## Troubleshooting

### Common Issues

#### Database connection failed
```
Error: Can't reach database server
```
**Solution:** Ensure database is running and `DATABASE_URL` is correct.

#### Port already in use
```
Error: listen EADDRINUSE: address already in use :::3000
```
**Solution:** Kill process on port or use different port:
```bash
lsof -i :3000  # Find process
kill -9 <PID>  # Kill it
```

#### Module not found
```
Error: Cannot find module 'xyz'
```
**Solution:** Clear node_modules and reinstall:
```bash
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

## Additional Resources

- [Framework Documentation](link)
- [API Documentation](./api-design.md)
- [Database Schema](./database-design.md)
- [Contributing Guide](../CONTRIBUTING.md)
```

---

**Template Version:** 1.0
**Used By:** appgen (Phase 7), webgen (Phase 6)
**Lines:** ~140
