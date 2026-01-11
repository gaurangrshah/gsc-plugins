# Testing Guide Template

Documentation template for test strategy, patterns, and coverage requirements.

## Testing Strategy

```markdown
# [Project Name] - Testing Guide

## Test Stack

- **Unit Tests:** Vitest
- **Component Tests:** Testing Library + Vitest
- **E2E Tests:** Playwright
- **API Tests:** Supertest (or Vitest)

## Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── lib/             # Utility function tests
│   └── server/          # Server logic tests
├── integration/         # Integration tests
│   ├── api/            # API endpoint tests
│   └── db/             # Database tests
├── e2e/                 # End-to-end tests
│   ├── auth.spec.ts
│   └── user-flow.spec.ts
└── fixtures/            # Shared test data
    ├── users.ts
    └── factories.ts
```

## Running Tests

```bash
# All tests
pnpm test

# Unit tests only
pnpm test:unit

# Integration tests
pnpm test:integration

# E2E tests
pnpm test:e2e

# Watch mode
pnpm test:watch

# Coverage report
pnpm test:coverage
```

## Writing Tests

### Unit Test Pattern
```typescript
import { describe, it, expect } from 'vitest'
import { calculateTotal } from '@/lib/pricing'

describe('calculateTotal', () => {
  it('should calculate total with tax', () => {
    const result = calculateTotal(100, 0.1)
    expect(result).toBe(110)
  })

  it('should handle zero amount', () => {
    const result = calculateTotal(0, 0.1)
    expect(result).toBe(0)
  })

  it('should throw for negative amounts', () => {
    expect(() => calculateTotal(-100, 0.1)).toThrow('Invalid amount')
  })
})
```

### Component Test Pattern
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '@/components/ui/button'

describe('Button', () => {
  it('should render with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })

  it('should call onClick when clicked', () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Click me</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('should be disabled when loading', () => {
    render(<Button loading>Click me</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### API Test Pattern
```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { createTestServer } from '@/tests/helpers'

describe('POST /api/users', () => {
  let server: TestServer

  beforeAll(async () => {
    server = await createTestServer()
  })

  afterAll(async () => {
    await server.close()
  })

  it('should create user with valid data', async () => {
    const response = await server.request('/api/users', {
      method: 'POST',
      body: { email: 'test@example.com', password: 'password123' }
    })

    expect(response.status).toBe(201)
    expect(response.body.data).toMatchObject({
      email: 'test@example.com'
    })
  })

  it('should reject invalid email', async () => {
    const response = await server.request('/api/users', {
      method: 'POST',
      body: { email: 'invalid', password: 'password123' }
    })

    expect(response.status).toBe(400)
    expect(response.body.error.code).toBe('VALIDATION_ERROR')
  })
})
```

### E2E Test Pattern
```typescript
import { test, expect } from '@playwright/test'

test.describe('User Registration', () => {
  test('should complete registration flow', async ({ page }) => {
    await page.goto('/register')

    await page.fill('[name="email"]', 'new@example.com')
    await page.fill('[name="password"]', 'securepass123')
    await page.fill('[name="name"]', 'Test User')
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByText('Welcome, Test User')).toBeVisible()
  })
})
```

## Test Fixtures & Factories

```typescript
// tests/fixtures/factories.ts
import { faker } from '@faker-js/faker'

export const createUser = (overrides = {}) => ({
  id: faker.string.uuid(),
  email: faker.internet.email(),
  name: faker.person.fullName(),
  createdAt: new Date(),
  ...overrides
})

export const createPost = (overrides = {}) => ({
  id: faker.string.uuid(),
  title: faker.lorem.sentence(),
  content: faker.lorem.paragraphs(3),
  published: false,
  ...overrides
})
```

## Coverage Requirements

| Category | Minimum | Target |
|----------|---------|--------|
| Statements | 70% | 85% |
| Branches | 65% | 80% |
| Functions | 70% | 85% |
| Lines | 70% | 85% |

### Critical Paths (100% coverage)
- Authentication flows
- Payment processing
- Data validation
- Security utilities

## CI Integration

```yaml
# .github/workflows/test.yml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: pnpm/action-setup@v2
    - run: pnpm install
    - run: pnpm test:coverage
    - uses: codecov/codecov-action@v3
```
```

---

**Template Version:** 1.0
**Used By:** appgen (Phase 6), webgen (Phase 5)
**Lines:** ~170
