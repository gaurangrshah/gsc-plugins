# API Design Template

Documentation template for REST/GraphQL API design and endpoint documentation.

## API Documentation

```markdown
# API Design: [Project Name]

**Base URL:** `https://api.example.com/v1`
**Auth:** [Bearer JWT | API Key | Session]
**Version:** v1

## Authentication

### Headers
```
Authorization: Bearer <token>
Content-Type: application/json
```

### Error Responses
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "status": 401
  }
}
```

## Endpoints

### Resource: Users

#### GET /users
List all users (paginated).

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 20 | Items per page |
| sort | string | created_at | Sort field |
| order | string | desc | Sort direction |

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

#### GET /users/:id
Get single user by ID.

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| id | UUID | User ID |

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "profile": { ... },
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

**Errors:**
- `404 Not Found` - User doesn't exist

#### POST /users
Create new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Validation:**
| Field | Rules |
|-------|-------|
| email | required, email format, unique |
| password | required, min 8 chars |
| name | required, max 100 chars |

**Response:** `201 Created`
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Errors:**
- `400 Bad Request` - Validation failed
- `409 Conflict` - Email already exists

#### PUT /users/:id
Update user.

#### DELETE /users/:id
Delete user.

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Missing or invalid auth |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource conflict |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /auth/* | 5 | 1 minute |
| GET /* | 100 | 1 minute |
| POST /* | 30 | 1 minute |

Headers returned:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640000000
```

## Webhooks

### Event: user.created
```json
{
  "event": "user.created",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```
```

## REST Conventions

| Action | Method | Path | Response |
|--------|--------|------|----------|
| List | GET | /resources | 200 + array |
| Get | GET | /resources/:id | 200 + object |
| Create | POST | /resources | 201 + object |
| Update | PUT | /resources/:id | 200 + object |
| Partial | PATCH | /resources/:id | 200 + object |
| Delete | DELETE | /resources/:id | 204 No Content |

---

**Template Version:** 1.0
**Used By:** appgen (Phase 4)
**Lines:** ~160
