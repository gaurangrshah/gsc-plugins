# Progressive Database Selection Framework

Decision framework for selecting appropriate database technology based on project requirements. Used when knowledge base has no explicit preference.

## Decision Tree

```
START: What type of data?
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

### Level 1: localStorage (Simplest)
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
