---
title: API Design Skill
type: skill
created: 2024-12-13
tags: [appgen, api, rest, design, endpoints]
---

# API Design Skill

Provides guidance for designing RESTful APIs with proper endpoints, authentication, and error handling.

## Purpose

This skill helps the appgen agent design sound API architectures with well-structured endpoints, input validation, and security.

---

## REST API Design Principles

### Resource Naming

**Use plural nouns for resources:**
- ✅ `/api/users`
- ❌ `/api/user`

**Use nesting for relationships:**
- ✅ `/api/users/:id/posts`
- ❌ `/api/user-posts?userId=:id`

**Keep URLs simple:**
- ✅ `/api/products`
- ❌ `/api/get-all-products`

### HTTP Methods

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve resources | `GET /api/users` |
| POST | Create resource | `POST /api/users` |
| PUT | Replace resource | `PUT /api/users/:id` |
| PATCH | Update fields | `PATCH /api/users/:id` |
| DELETE | Delete resource | `DELETE /api/users/:id` |

---

## Standard Endpoints

### List Resources

```
GET /api/users?page=1&limit=10&sort=name&order=asc
```

**Query Parameters:**
- `page` (number) - Page number (default: 1)
- `limit` (number) - Items per page (default: 10, max: 100)
- `sort` (string) - Field to sort by
- `order` (asc|desc) - Sort direction

**Response:**
```json
{
  "data": [
    { "id": "1", "name": "Alice", "email": "alice@example.com" },
    { "id": "2", "name": "Bob", "email": "bob@example.com" }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 42,
    "totalPages": 5
  }
}
```

### Get Single Resource

```
GET /api/users/:id
```

**Response:**
```json
{
  "data": {
    "id": "1",
    "name": "Alice",
    "email": "alice@example.com",
    "createdAt": "2024-01-15T10:00:00Z"
  }
}
```

### Create Resource

```
POST /api/users
Content-Type: application/json

{
  "name": "Alice",
  "email": "alice@example.com"
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "1",
    "name": "Alice",
    "email": "alice@example.com",
    "createdAt": "2024-01-15T10:00:00Z"
  }
}
```

### Update Resource

```
PATCH /api/users/:id
Content-Type: application/json

{
  "name": "Alice Smith"
}
```

**Response:**
```json
{
  "data": {
    "id": "1",
    "name": "Alice Smith",
    "email": "alice@example.com",
    "updatedAt": "2024-01-15T11:00:00Z"
  }
}
```

### Delete Resource

```
DELETE /api/users/:id
```

**Response (204 No Content):**
Empty body

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request body",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., email already exists) |
| 422 | Unprocessable Entity | Business logic error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

### Error Code Examples

```typescript
// Validation error (400)
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request body",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}

// Unauthorized (401)
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}

// Forbidden (403)
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}

// Not found (404)
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}

// Conflict (409)
{
  "error": {
    "code": "DUPLICATE_EMAIL",
    "message": "Email already in use"
  }
}

// Server error (500)
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

---

## Input Validation with Zod

### Define Schemas

```typescript
import { z } from 'zod';

// Create user schema
export const createUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  role: z.enum(['USER', 'ADMIN']).default('USER'),
});

// Update user schema (all fields optional)
export const updateUserSchema = createUserSchema.partial();

// Query parameters schema
export const listUsersQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(10),
  sort: z.enum(['name', 'createdAt']).default('createdAt'),
  order: z.enum(['asc', 'desc']).default('desc'),
});
```

### Validate in Route Handlers

```typescript
// Hono example
app.post('/api/users', async (c) => {
  try {
    // Parse and validate request body
    const body = await c.req.json();
    const data = createUserSchema.parse(body);

    // Create user
    const user = await prisma.user.create({ data });

    return c.json({ data: user }, 201);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return c.json({
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid request body',
          details: error.errors.map(e => ({
            field: e.path.join('.'),
            message: e.message,
          })),
        },
      }, 400);
    }
    throw error;
  }
});
```

---

## Authentication Strategy

### JWT Authentication

**Endpoints:**

```
POST /api/auth/register     # Create account
POST /api/auth/login        # Get JWT token
POST /api/auth/refresh      # Refresh token
GET  /api/auth/me           # Get current user (protected)
```

**Login Flow:**

```typescript
// POST /api/auth/login
{
  "email": "alice@example.com",
  "password": "secure123"
}

// Response (200)
{
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 3600,  // seconds
    "user": {
      "id": "1",
      "name": "Alice",
      "email": "alice@example.com"
    }
  }
}
```

**Protected Endpoint:**

```typescript
// Middleware to verify JWT
export async function authMiddleware(c: Context, next: Next) {
  const authHeader = c.req.header('Authorization');

  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({
      error: {
        code: 'UNAUTHORIZED',
        message: 'Authentication required',
      },
    }, 401);
  }

  const token = authHeader.substring(7);

  try {
    const payload = await verifyJWT(token);
    c.set('userId', payload.userId);
    await next();
  } catch (error) {
    return c.json({
      error: {
        code: 'INVALID_TOKEN',
        message: 'Invalid or expired token',
      },
    }, 401);
  }
}

// Use middleware
app.get('/api/users/:id', authMiddleware, async (c) => {
  const userId = c.get('userId');  // From middleware
  const targetId = c.req.param('id');

  // Check authorization
  if (userId !== targetId) {
    return c.json({
      error: {
        code: 'FORBIDDEN',
        message: 'Cannot access other users',
      },
    }, 403);
  }

  // Fetch user...
});
```

---

## Authorization Patterns

### Role-Based Access Control (RBAC)

```typescript
// Middleware for admin-only routes
export async function adminOnly(c: Context, next: Next) {
  const userId = c.get('userId');

  const user = await prisma.user.findUnique({
    where: { id: userId },
  });

  if (user?.role !== 'ADMIN') {
    return c.json({
      error: {
        code: 'FORBIDDEN',
        message: 'Admin access required',
      },
    }, 403);
  }

  await next();
}

// Admin-only endpoint
app.delete('/api/users/:id', authMiddleware, adminOnly, async (c) => {
  // Delete user...
});
```

### Resource Ownership

```typescript
// Ensure user owns the resource
app.patch('/api/posts/:id', authMiddleware, async (c) => {
  const userId = c.get('userId');
  const postId = c.req.param('id');

  const post = await prisma.post.findUnique({
    where: { id: postId },
  });

  if (!post) {
    return c.json({
      error: { code: 'NOT_FOUND', message: 'Post not found' },
    }, 404);
  }

  if (post.authorId !== userId) {
    return c.json({
      error: { code: 'FORBIDDEN', message: 'Not your post' },
    }, 403);
  }

  // Update post...
});
```

---

## API Design Checklist

Before finalizing API design:

### Endpoints
- [ ] All CRUD operations defined for each resource
- [ ] URLs use plural nouns
- [ ] Nested resources use proper nesting
- [ ] HTTP methods correct (GET, POST, PATCH, DELETE)

### Request Validation
- [ ] All inputs validated with Zod schemas
- [ ] Query parameters validated
- [ ] Path parameters validated
- [ ] Request body validated

### Response Format
- [ ] Consistent response structure (`{ data: ... }`)
- [ ] List endpoints include pagination
- [ ] Error responses follow standard format
- [ ] Proper HTTP status codes

### Authentication
- [ ] Auth strategy defined (JWT, session, OAuth)
- [ ] Protected endpoints identified
- [ ] Public endpoints identified
- [ ] Token refresh strategy (if JWT)

### Authorization
- [ ] User can only access their own data
- [ ] Admin-only endpoints protected
- [ ] Resource ownership checked

### Error Handling
- [ ] Validation errors return 400
- [ ] Auth errors return 401 or 403
- [ ] Not found errors return 404
- [ ] Server errors return 500
- [ ] Error messages don't leak sensitive info

---

## Documentation Template

Save API documentation to `api/design.md`:

```markdown
# API Design

## Base URL

\`\`\`
http://localhost:3000/api/v1
\`\`\`

## Authentication

All protected endpoints require a JWT token in the Authorization header:

\`\`\`
Authorization: Bearer <token>
\`\`\`

## Endpoints

### Authentication

#### Register
\`\`\`
POST /auth/register
\`\`\`

**Request Body:**
\`\`\`json
{
  "name": "Alice",
  "email": "alice@example.com",
  "password": "secure123"
}
\`\`\`

**Response (201):**
[Example response...]

#### Login
\`\`\`
POST /auth/login
\`\`\`

[Continue for each endpoint...]

### Users

#### List Users
\`\`\`
GET /users?page=1&limit=10
\`\`\`

**Auth:** Required
**Query Params:**
- \`page\` (number, default: 1)
- \`limit\` (number, default: 10, max: 100)

**Response (200):**
[Example response...]

[Continue for each resource...]

## Error Responses

[Document error format and codes...]
```

---

## Version History

**v1.0** (2024-12-13)
- Initial skill for appgen plugin
- REST API design principles
- Input validation with Zod
- Authentication strategies
- Authorization patterns
- Error handling standards
