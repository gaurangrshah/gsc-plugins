---
title: Database Design Skill
type: skill
created: 2024-12-13
tags: [appgen, database, prisma, drizzle, schema]
---

# Database Design Skill

Provides guidance for designing database schemas for full-stack applications.

## Purpose

This skill helps the appgen agent design sound database schemas with proper relationships, types, constraints, and indexes.

---

## Schema Design Process

### 1. Entity Identification

Extract entities from requirements:

**Example Requirement:** "Inventory management system for a warehouse"

**Entities:**
- User (warehouse staff)
- Product (items in inventory)
- Category (product categories)
- Location (warehouse locations)
- InventoryTransaction (stock movements)

### 2. Attribute Definition

For each entity, define:
- **ID:** Primary key (usually String cuid() or Int autoincrement())
- **Required fields:** Cannot be null
- **Optional fields:** Can be null (marked with `?`)
- **Timestamps:** createdAt, updatedAt
- **Constraints:** Unique, default values

**Example:**
```prisma
model Product {
  id          String   @id @default(cuid())
  name        String
  sku         String   @unique
  description String?
  quantity    Int      @default(0)
  categoryId  String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
```

### 3. Relationship Mapping

Identify relationships:

**One-to-Many:**
- One Category has many Products
- One User has many InventoryTransactions

**Many-to-Many:**
- Products can be in multiple Locations
- Locations can have multiple Products

**Prisma Syntax:**

**One-to-Many:**
```prisma
model Category {
  id       String    @id @default(cuid())
  name     String
  products Product[]  // Array on "many" side
}

model Product {
  id         String   @id @default(cuid())
  categoryId String
  category   Category @relation(fields: [categoryId], references: [id])
}
```

**Many-to-Many (Explicit Join Table):**
```prisma
model Product {
  id        String            @id @default(cuid())
  locations ProductLocation[]
}

model Location {
  id       String            @id @default(cuid())
  products ProductLocation[]
}

model ProductLocation {
  productId  String
  locationId String
  quantity   Int
  product    Product  @relation(fields: [productId], references: [id])
  location   Location @relation(fields: [locationId], references: [id])

  @@id([productId, locationId])
  @@index([productId])
  @@index([locationId])
}
```

### 4. Index Planning

Add indexes for:
- Foreign keys (always)
- Frequently queried columns
- Unique constraints

**Example:**
```prisma
model Product {
  id         String   @id @default(cuid())
  sku        String   @unique
  categoryId String
  category   Category @relation(fields: [categoryId], references: [id])

  @@index([categoryId])  // Index on foreign key
  @@index([sku])         // Index on frequently searched field
}
```

---

## Prisma Schema Reference

### Data Types

| Prisma Type | Database Type | Use Case |
|-------------|---------------|----------|
| `String` | VARCHAR | Text fields, IDs |
| `Int` | INTEGER | Numbers, counts |
| `BigInt` | BIGINT | Large numbers |
| `Float` | DOUBLE | Decimals |
| `Decimal` | DECIMAL | Money (precise) |
| `Boolean` | BOOLEAN | True/false |
| `DateTime` | TIMESTAMP | Dates and times |
| `Json` | JSON | Unstructured data |

### Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `@id` | Primary key | `id String @id` |
| `@default()` | Default value | `@default(cuid())` |
| `@unique` | Unique constraint | `email String @unique` |
| `@updatedAt` | Auto-update timestamp | `updatedAt DateTime @updatedAt` |
| `@relation()` | Foreign key | `@relation(fields: [userId], references: [id])` |
| `@@index()` | Index | `@@index([email])` |
| `@@unique()` | Composite unique | `@@unique([email, tenantId])` |

### Default Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `cuid()` | Random ID (short) | `@default(cuid())` |
| `uuid()` | Random ID (standard) | `@default(uuid())` |
| `autoincrement()` | Auto-increment number | `@default(autoincrement())` |
| `now()` | Current timestamp | `@default(now())` |

---

## Common Patterns

### User Authentication

```prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  passwordHash  String    // Use bcrypt or argon2
  name          String?
  emailVerified DateTime?
  image         String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  sessions Session[]
  accounts Account[]

  @@index([email])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
}
```

### Multi-Tenancy

```prisma
model Tenant {
  id    String @id @default(cuid())
  name  String
  users User[]
}

model User {
  id       String @id @default(cuid())
  email    String
  tenantId String
  tenant   Tenant @relation(fields: [tenantId], references: [id])

  @@unique([email, tenantId])  // Email unique per tenant
  @@index([tenantId])
}
```

### Soft Deletes

```prisma
model Product {
  id        String    @id @default(cuid())
  name      String
  deletedAt DateTime?  // Null = not deleted
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt

  @@index([deletedAt])
}
```

### Audit Trail

```prisma
model Product {
  id        String   @id @default(cuid())
  name      String
  createdBy String
  updatedBy String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  creator User @relation("ProductCreator", fields: [createdBy], references: [id])
  updater User? @relation("ProductUpdater", fields: [updatedBy], references: [id])

  @@index([createdBy])
  @@index([updatedBy])
}
```

---

## Schema Design Checklist

Before finalizing a schema:

### Structure
- [ ] All entities identified from requirements
- [ ] All required fields present
- [ ] Optional fields marked with `?`
- [ ] Primary keys defined (`@id`)
- [ ] Timestamps included (createdAt, updatedAt)

### Relationships
- [ ] All relationships identified
- [ ] One-to-many use scalar field + relation field
- [ ] Many-to-many use explicit join tables
- [ ] Foreign key fields match referenced type
- [ ] Cascade delete rules appropriate (`onDelete: Cascade`)

### Constraints
- [ ] Unique constraints on unique fields
- [ ] Default values where appropriate
- [ ] Enums for fixed sets of values

### Indexes
- [ ] Indexes on all foreign keys
- [ ] Indexes on frequently queried fields
- [ ] Composite indexes for multi-column queries

### Security
- [ ] No sensitive data in plain text
- [ ] Password fields named `passwordHash` (not `password`)
- [ ] Email verification fields if needed

---

## Migration Strategy

### Initial Migration

```bash
# Generate Prisma client
npx prisma generate

# Create initial migration
npx prisma migrate dev --name init

# Apply migration
npx prisma migrate deploy
```

### Schema Changes

1. Modify schema.prisma
2. Run `npx prisma migrate dev --name description_of_change`
3. Review generated migration file
4. Test migration on development database

### Seed Data

Create `prisma/seed.ts`:

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Create seed data
  const category = await prisma.category.create({
    data: {
      name: 'Electronics',
    },
  });

  console.log({ category });
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

Add to package.json:
```json
{
  "prisma": {
    "seed": "tsx prisma/seed.ts"
  }
}
```

---

## Drizzle Alternative

If using Drizzle instead of Prisma:

```typescript
// schema.ts
import { pgTable, text, timestamp, integer, index } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: text('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  emailIdx: index('email_idx').on(table.email),
}));

export const posts = pgTable('posts', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content').notNull(),
  authorId: text('author_id').notNull().references(() => users.id),
  createdAt: timestamp('created_at').defaultNow(),
}, (table) => ({
  authorIdx: index('author_idx').on(table.authorId),
}));
```

---

## Documentation Template

Save schema documentation to `database/schema.md`:

```markdown
# Database Schema

## Overview

[Brief description of the database purpose]

## Entities

### User

Represents warehouse staff members.

**Fields:**
- \`id\` (String) - Primary key
- \`email\` (String) - Unique email address
- \`name\` (String) - Full name
- \`role\` (Enum) - USER | ADMIN
- \`createdAt\` (DateTime) - Account creation date
- \`updatedAt\` (DateTime) - Last update date

**Relationships:**
- Has many InventoryTransactions

**Indexes:**
- email

### Product

Represents items in the warehouse inventory.

[Continue for each entity...]

## Relationships

- User → InventoryTransaction (one-to-many)
- Category → Product (one-to-many)
- Product ↔ Location (many-to-many via ProductLocation)

## Migrations

### Initial Schema (YYYY-MM-DD)

Created base schema with User, Product, Category, Location, InventoryTransaction entities.

[Document each migration...]
```

---

## Common Mistakes to Avoid

1. **Missing indexes on foreign keys** - Always add `@@index([foreignKeyId])`
2. **Array index as keys** - Use stable IDs for keys, not array positions
3. **No cascade delete** - Decide if related records should be deleted
4. **Missing timestamps** - Always include createdAt and updatedAt
5. **Ambiguous relationship names** - Use clear names for self-relations
6. **No unique constraints** - Add @unique on emails, SKUs, etc.
7. **Wrong relationship type** - Many-to-many needs join table, not one-to-many

---

## Version History

**v1.0** (2024-12-13)
- Initial skill for appgen plugin
- Prisma schema patterns
- Drizzle alternative syntax
- Migration strategies
- Common patterns and checklist
