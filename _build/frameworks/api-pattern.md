# Progressive API Pattern Framework

Decision framework for selecting API architecture based on project requirements. Used when knowledge base has no explicit preference.

## Decision Tree

```
START: What type of API do you need?
│
├─► Server-to-browser (same app) → Server Actions / tRPC
│   │
│   ├─► Next.js App Router → Server Actions
│   │   • Simplest
│   │   • Type-safe by default
│   │   • No API layer needed
│   │
│   └─► Need client-side calls → tRPC
│       • End-to-end type safety
│       • React Query integration
│       • Works with any framework
│
├─► Public API / Third-party consumers → REST or GraphQL
│   │
│   ├─► Simple CRUD, many clients → REST
│   │   • Universal understanding
│   │   • Easy to cache
│   │   • OpenAPI documentation
│   │
│   └─► Complex queries, flexible needs → GraphQL
│       • Client-driven queries
│       • Single endpoint
│       • Schema documentation
│
├─► Real-time / Streaming → WebSockets / SSE
│   │
│   ├─► Bi-directional → WebSockets (Socket.io)
│   └─► Server push only → Server-Sent Events (SSE)
│
└─► Microservices / Internal → gRPC or REST
    │
    ├─► High performance → gRPC
    └─► Simple/compatible → REST with OpenAPI
```

## Progressive Complexity Scale

### Level 1: Server Actions (Simplest)
**Use when:**
- Next.js App Router
- Same-origin requests only
- Form submissions
- Simple mutations

```typescript
// actions.ts
'use server'

export async function createUser(formData: FormData) {
  const email = formData.get('email') as string
  const user = await db.user.create({ data: { email } })
  revalidatePath('/users')
  return user
}

// In component
<form action={createUser}>
  <input name="email" type="email" />
  <button type="submit">Create</button>
</form>
```

**Upgrade trigger:** Need client-side calls, complex state, external consumers

---

### Level 2: tRPC (Type-Safe Internal)
**Use when:**
- Full-stack TypeScript
- Complex client-side state
- Need React Query features
- Internal API only

```typescript
// server/routers/user.ts
export const userRouter = router({
  list: publicProcedure.query(async () => {
    return db.user.findMany()
  }),
  create: protectedProcedure
    .input(z.object({ email: z.string().email() }))
    .mutation(async ({ input }) => {
      return db.user.create({ data: input })
    })
})

// Client usage
const users = trpc.user.list.useQuery()
const createUser = trpc.user.create.useMutation()
```

**Upgrade trigger:** External API consumers, non-TypeScript clients

---

### Level 3: REST API (Standard)
**Use when:**
- External API consumers
- Mobile app backend
- Third-party integrations
- Need caching (CDN)

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const users = await db.user.findMany()
  return NextResponse.json({ data: users })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const user = await db.user.create({ data: body })
  return NextResponse.json({ data: user }, { status: 201 })
}
```

**Upgrade trigger:** Complex nested queries, bandwidth optimization

---

### Level 4: GraphQL (Flexible Queries)
**Use when:**
- Multiple client types
- Complex data relationships
- Need query flexibility
- Bandwidth optimization

```typescript
// With GraphQL Yoga
const typeDefs = /* GraphQL */ `
  type User {
    id: ID!
    email: String!
    posts: [Post!]!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
  }

  type Mutation {
    createUser(email: String!): User!
  }
`

const resolvers = {
  Query: {
    users: () => db.user.findMany(),
    user: (_, { id }) => db.user.findUnique({ where: { id } })
  }
}
```

## Quick Decision Matrix

| Requirement | Server Actions | tRPC | REST | GraphQL |
|-------------|----------------|------|------|---------|
| Setup complexity | None | Low | Medium | High |
| Type safety | Good | Best | Manual | Good |
| External clients | ❌ | ❌ | ✅ | ✅ |
| Caching | Auto | RQ | HTTP | Complex |
| Documentation | ❌ | Auto | OpenAPI | Schema |
| Learning curve | Low | Low | Low | High |
| Bundle size | None | Small | None | Medium |
| Real-time | ❌ | Subscription | ❌ | Subscription |

## API Design Best Practices

### REST Conventions
```
GET    /api/users          # List
GET    /api/users/:id      # Get one
POST   /api/users          # Create
PUT    /api/users/:id      # Update (full)
PATCH  /api/users/:id      # Update (partial)
DELETE /api/users/:id      # Delete

# Nested resources
GET    /api/users/:id/posts
POST   /api/users/:id/posts
```

### Response Format
```typescript
// Success
{
  "data": { ... },
  "meta": { "page": 1, "total": 100 }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [{ "field": "email", "message": "Required" }]
  }
}
```

### Versioning Strategy
```
URL versioning:     /api/v1/users (recommended)
Header versioning:  Accept: application/vnd.api+json;version=1
Query versioning:   /api/users?version=1
```

## Real-Time Patterns

### Server-Sent Events (Simple)
```typescript
// For notifications, live updates
export async function GET() {
  const stream = new ReadableStream({
    start(controller) {
      const interval = setInterval(() => {
        controller.enqueue(`data: ${JSON.stringify({ time: Date.now() })}\n\n`)
      }, 1000)

      return () => clearInterval(interval)
    }
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' }
  })
}
```

### WebSockets (Bi-directional)
```typescript
// For chat, collaboration
import { Server } from 'socket.io'

const io = new Server(server)
io.on('connection', (socket) => {
  socket.on('message', (data) => {
    io.emit('message', data)
  })
})
```

## Default Recommendation

**For most Next.js applications:** Server Actions + REST for external

```
Rationale:
• Server Actions for internal mutations (simpler)
• REST API routes for external consumers
• Avoids over-engineering
• Easy to evolve
• Well-documented patterns
```

---

**Framework Version:** 1.0
**Used By:** appgen (API implementation phase)
