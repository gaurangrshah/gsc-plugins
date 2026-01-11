# Progressive Database Selection Framework

Decision framework for selecting appropriate database technology based on project requirements. Used when knowledge base has no explicit preference.

## First Question (When No Preference Specified)

**Before selecting a database, ask the user:**

> "Would you like to stub the database layer for now using the adapter pattern?
> This lets you build features faster and defer the database decision until requirements are clearer."

Options:
1. **Yes, stub it** → Use Level 0 (in-memory adapter)
2. **No, choose now** → Continue to decision tree below

## Decision Tree

```
START: Stub or real database?
│
├─► Stub for now (fastest) → Level 0: Adapter Pattern
│   • Build features without DB setup
│   • Swap implementation later
│   • Perfect for prototypes/MVPs
│
└─► Real database → What type of data?
    │
    ├─► Structured, relational → SQL Database
│   │
│   ├─► Embedded/local app → SQLite
│   │   • Single user
│   │   • Desktop/mobile app
│   │   • Serverless functions
│   │   • Development/testing
│   │
│   ├─► Web app, <100K users → PostgreSQL
│   │   • Full ACID compliance
│   │   • Complex queries
│   │   • JSON support needed
│   │   • Geospatial data
│   │
│   └─► Enterprise, >100K users → PostgreSQL + Read Replicas
│       • High availability
│       • Global distribution
│       • Consider: CockroachDB, PlanetScale
│
├─► Documents, flexible schema → Document Database
│   │
│   ├─► Rapid prototyping → MongoDB
│   ├─► Serverless first → MongoDB Atlas / Fauna
│   └─► Need transactions → MongoDB 4.0+ / FerretDB
│
├─► Key-value, caching → Redis
│   • Session storage
│   • Rate limiting
│   • Real-time leaderboards
│   • Pub/sub messaging
│
├─► Time-series data → TimescaleDB / InfluxDB
│   • IoT sensor data
│   • Metrics/monitoring
│   • Financial data
│
└─► Search-heavy → Elasticsearch / Meilisearch
    • Full-text search
    • Faceted navigation
    • Log aggregation
```

## Progressive Complexity Scale

### Level 0: Stub with Adapter Pattern (Fastest Start)
**Use when:**
- Rapid prototyping / MVP
- Requirements still unclear
- Want to defer DB decision
- Focus on business logic first

**Pattern:** Define a repository interface, implement with in-memory storage.

```typescript
// types/repository.ts - Define the contract
interface UserRepository {
  findById(id: string): Promise<User | null>
  findByEmail(email: string): Promise<User | null>
  create(data: CreateUserInput): Promise<User>
  update(id: string, data: UpdateUserInput): Promise<User>
  delete(id: string): Promise<void>
}

// lib/repositories/user-stub.ts - In-memory implementation
class UserStubRepository implements UserRepository {
  private users: Map<string, User> = new Map()

  async findById(id: string): Promise<User | null> {
    return this.users.get(id) ?? null
  }

  async findByEmail(email: string): Promise<User | null> {
    return [...this.users.values()].find(u => u.email === email) ?? null
  }

  async create(data: CreateUserInput): Promise<User> {
    const user: User = {
      id: crypto.randomUUID(),
      ...data,
      createdAt: new Date(),
      updatedAt: new Date()
    }
    this.users.set(user.id, user)
    return user
  }

  async update(id: string, data: UpdateUserInput): Promise<User> {
    const user = this.users.get(id)
    if (!user) throw new Error('User not found')
    const updated = { ...user, ...data, updatedAt: new Date() }
    this.users.set(id, updated)
    return updated
  }

  async delete(id: string): Promise<void> {
    this.users.delete(id)
  }
}

// lib/repositories/index.ts - Factory for swapping implementations
export function createUserRepository(): UserRepository {
  // Swap this line when ready for real DB
  return new UserStubRepository()
  // return new UserPrismaRepository(prisma)
  // return new UserDrizzleRepository(db)
}
```

**Benefits:**
- Zero setup time - start coding immediately
- Tests run fast (no DB connection)
- Easy to swap implementation later
- Business logic stays unchanged

**Upgrade trigger:** Need data persistence, multiple users, production deployment

---

### Level 1: localStorage (Client-Side Only)
**Use when:**
- Client-side only data
- User preferences
- Draft content
- No server needed

```typescript
// Simple key-value
localStorage.setItem('theme', 'dark')
const theme = localStorage.getItem('theme')
```

**Upgrade trigger:** Need server-side access, data persistence across devices

---

### Level 2: SQLite (Simple Server)
**Use when:**
- Single server deployment
- <10K concurrent users
- Simple queries
- File-based backup is fine

```typescript
// With Drizzle
import { drizzle } from 'drizzle-orm/better-sqlite3'
import Database from 'better-sqlite3'

const sqlite = new Database('app.db')
const db = drizzle(sqlite)
```

**Upgrade trigger:** Multiple servers, high concurrency, need replication

---

### Level 3: PostgreSQL (Production Standard)
**Use when:**
- Production web applications
- Complex data relationships
- Need ACID guarantees
- Advanced features (JSON, arrays, full-text)

```typescript
// With Prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
```

**Upgrade trigger:** Global distribution, extreme scale, specific workload needs

---

### Level 4: Specialized (Scale/Workload)
**Use when:**
- Specific performance requirements
- Global distribution needed
- Specialized data patterns

| Workload | Solution |
|----------|----------|
| Global SQL | CockroachDB, PlanetScale |
| High-volume writes | ScyllaDB, Cassandra |
| Real-time sync | Supabase, Firebase |
| Edge-first | Turso, D1 |

## Quick Decision Matrix

| Requirement | SQLite | PostgreSQL | MongoDB | Redis |
|-------------|--------|------------|---------|-------|
| ACID | ✅ | ✅ | Partial | ❌ |
| Relational | ✅ | ✅ | ❌ | ❌ |
| Horizontal scale | ❌ | ✅ | ✅ | ✅ |
| Flexible schema | ❌ | Partial | ✅ | ✅ |
| Full-text search | Basic | ✅ | ✅ | ❌ |
| Geospatial | ❌ | ✅ | ✅ | ✅ |
| Time-series | ❌ | ✅* | ❌ | ❌ |
| Caching | ❌ | ❌ | ❌ | ✅ |
| Setup complexity | Low | Medium | Medium | Low |
| Hosting cost | Free | $$ | $$ | $ |

*With TimescaleDB extension

## ORM Selection

| Database | Recommended ORM | Alternative |
|----------|-----------------|-------------|
| PostgreSQL | Prisma | Drizzle |
| SQLite | Drizzle | Prisma |
| MongoDB | Mongoose | Prisma |
| Any SQL | Drizzle | Kysely |

## Default Recommendation

**For most web applications:** PostgreSQL + Prisma

```
Rationale:
• Battle-tested at scale (Instagram, Discord, Notion)
• Excellent tooling ecosystem
• Easy migration path from SQLite
• JSON support bridges SQL/NoSQL gap
• Managed options: Supabase, Neon, Railway
```

---

**Framework Version:** 1.0
**Used By:** appgen, webgen (database selection phase)
