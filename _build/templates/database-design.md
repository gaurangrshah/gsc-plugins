# Database Design Template

Documentation template for database schema design and architecture decisions.

## Schema Documentation

```markdown
# Database Design: [Project Name]

**Database:** [PostgreSQL | SQLite | MySQL | MongoDB]
**ORM:** [Prisma | Drizzle | TypeORM | None]
**Version:** [Schema version]

## Entity Relationship Diagram

```
[User] 1───* [Post] *───* [Tag]
   │            │
   │            └──1───* [Comment]
   │
   └──1───1 [Profile]
```

## Tables/Collections

### users
Primary user account table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Primary key |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hash |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update |

**Indexes:**
- `idx_users_email` on (email) - Login lookups
- `idx_users_created` on (created_at) - Recent users

**Relationships:**
- Has many: posts, comments
- Has one: profile

### [table_name]
[Description]

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ... | ... | ... | ... |

## Migrations

### Migration Naming Convention
```
YYYYMMDDHHMMSS_description.sql
```

### Migration Template
```sql
-- Migration: [description]
-- Created: [date]

-- Up
ALTER TABLE [table] ADD COLUMN [column] [type];

-- Down
ALTER TABLE [table] DROP COLUMN [column];
```

## Query Patterns

### Common Queries

#### Get user with posts
```sql
SELECT u.*, json_agg(p.*) as posts
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
WHERE u.id = $1
GROUP BY u.id;
```

#### Paginated list
```sql
SELECT * FROM posts
WHERE published = true
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;
```

### Query Performance Notes
- [Note about indexing strategy]
- [Note about N+1 prevention]

## Data Integrity

### Constraints
- Foreign keys with ON DELETE behavior
- Check constraints for valid values
- Unique constraints for business rules

### Validation Rules
| Field | Rule | Enforcement |
|-------|------|-------------|
| email | Valid email format | Application + DB |
| password | Min 8 chars | Application |
| status | Enum values | DB CHECK |

## Backup & Recovery

### Backup Strategy
- Full backup: [frequency]
- Incremental: [frequency]
- Retention: [period]

### Recovery Procedures
1. [Step 1]
2. [Step 2]
```

## Quick Reference

### PostgreSQL Types Cheatsheet
| Use Case | Type | Notes |
|----------|------|-------|
| ID | UUID | Use uuid_generate_v4() |
| Short text | VARCHAR(n) | Enforce max length |
| Long text | TEXT | No length limit |
| Integer | INTEGER | 4 bytes |
| Big integer | BIGINT | 8 bytes |
| Decimal | NUMERIC(p,s) | Exact precision |
| Boolean | BOOLEAN | true/false |
| Timestamp | TIMESTAMPTZ | Always with timezone |
| JSON | JSONB | Binary, indexable |
| Array | TYPE[] | Native arrays |

### Index Strategy
| Query Pattern | Index Type |
|---------------|------------|
| Equality | B-tree (default) |
| Range | B-tree |
| Full text | GIN |
| JSON | GIN |
| Geospatial | GiST |

---

**Template Version:** 1.0
**Used By:** appgen (Phase 3), webgen (if DB needed)
**Lines:** ~140
