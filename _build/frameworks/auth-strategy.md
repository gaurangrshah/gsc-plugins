# Progressive Auth Strategy Framework

Decision framework for selecting authentication approach based on project requirements. Used when knowledge base has no explicit preference.

## First Question (When No Preference Specified)

**Before selecting an auth strategy, ask the user:**

> "Would you like to stub authentication for now using the adapter pattern?
> This lets you build protected routes and user features without setting up auth infrastructure yet."

Options:
1. **Yes, stub it** → Use Level 0 (mock auth adapter)
2. **No, choose now** → Continue to decision tree below

## Decision Tree

```
START: Stub or real auth?
│
├─► Stub for now (fastest) → Level 0: Adapter Pattern
│   • Build protected features without auth setup
│   • Swap implementation later
│   • Perfect for prototypes/MVPs
│
└─► Real auth → What type of auth do you need?
    │
    ├─► Simple email/password → Auth.js (NextAuth)
│   │
│   ├─► + Social logins → Auth.js with providers
│   ├─► + Magic links → Auth.js + Resend
│   └─► + 2FA → Auth.js + custom TOTP
│
├─► Managed/hosted auth → Clerk or Auth0
│   │
│   ├─► Startup, quick launch → Clerk
│   │   • Best DX
│   │   • Pre-built components
│   │   • Generous free tier
│   │
│   └─► Enterprise, compliance → Auth0
│       • SOC2, HIPAA
│       • Custom domains
│       • Advanced rules
│
├─► Self-hosted, full control → Lucia or Custom
│   │
│   ├─► Type-safe, modern → Lucia
│   └─► Legacy/specific needs → Custom JWT/Session
│
└─► Backend/API only → JWT or API Keys
    │
    ├─► User-facing API → JWT with refresh tokens
    └─► Service-to-service → API Keys or mTLS
```

## Progressive Complexity Scale

### Level 0: Stub with Adapter Pattern (Fastest Start)
**Use when:**
- Rapid prototyping / MVP
- Requirements still unclear
- Want to defer auth decision
- Focus on features first

**Pattern:** Define an auth interface, implement with mock user.

```typescript
// types/auth.ts - Define the contract
interface AuthService {
  getCurrentUser(): Promise<User | null>
  login(credentials: LoginInput): Promise<User>
  logout(): Promise<void>
  isAuthenticated(): Promise<boolean>
  requireAuth(): Promise<User>  // Throws if not authenticated
}

interface User {
  id: string
  email: string
  name: string
  role: 'user' | 'admin'
}

// lib/auth/auth-stub.ts - Mock implementation
class AuthStubService implements AuthService {
  private currentUser: User | null = {
    id: 'stub-user-1',
    email: 'dev@example.com',
    name: 'Dev User',
    role: 'admin'  // Full access for development
  }

  async getCurrentUser(): Promise<User | null> {
    return this.currentUser
  }

  async login(credentials: LoginInput): Promise<User> {
    // Accept any credentials in stub mode
    this.currentUser = {
      id: 'stub-user-1',
      email: credentials.email,
      name: 'Dev User',
      role: 'admin'
    }
    return this.currentUser
  }

  async logout(): Promise<void> {
    this.currentUser = null
  }

  async isAuthenticated(): Promise<boolean> {
    return this.currentUser !== null
  }

  async requireAuth(): Promise<User> {
    if (!this.currentUser) {
      throw new Error('Not authenticated')
    }
    return this.currentUser
  }
}

// lib/auth/index.ts - Factory for swapping implementations
export function createAuthService(): AuthService {
  if (process.env.NODE_ENV === 'development' && process.env.STUB_AUTH) {
    return new AuthStubService()
  }
  // Swap when ready for real auth
  // return new AuthJsService()
  // return new ClerkAuthService()
  return new AuthStubService()  // Default to stub for now
}

// Usage in components/server actions
import { createAuthService } from '@/lib/auth'

const auth = createAuthService()

export async function protectedAction() {
  const user = await auth.requireAuth()
  // ... do protected stuff
}
```

**Benefits:**
- Zero setup time - start building immediately
- No OAuth apps, no env vars needed
- Easy to test different user roles
- Business logic stays unchanged when swapping

**Upgrade trigger:** Need real users, production deployment, OAuth/social login

---

### Level 1: Session-Only (Simple Real Auth)
**Use when:**
- Internal tools
- Simple production needs
- Single trusted domain

```typescript
// Simple cookie session
import { cookies } from 'next/headers'

export async function login(userId: string) {
  cookies().set('session', userId, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax'
  })
}
```

**Upgrade trigger:** Need OAuth, magic links, multiple providers

---

### Level 2: Auth.js (Standard)
**Use when:**
- Production web apps
- Need OAuth providers
- Want battle-tested solution
- Self-hosted preference

```typescript
// auth.ts
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'
import Credentials from 'next-auth/providers/credentials'

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    GitHub,
    Credentials({
      credentials: {
        email: {},
        password: {}
      },
      authorize: async (credentials) => {
        // Verify credentials
        return user
      }
    })
  ]
})
```

**Upgrade trigger:** Need pre-built UI, user management, organization features

---

### Level 3: Managed Auth (Convenience)
**Use when:**
- Want hosted solution
- Need user management UI
- Organization/team features
- Compliance requirements

**Tool:** Clerk

```typescript
// middleware.ts
import { clerkMiddleware } from '@clerk/nextjs/server'
export default clerkMiddleware()

// In component
import { SignInButton, UserButton } from '@clerk/nextjs'
```

**Upgrade trigger:** Cost concerns at scale, need full control

---

### Level 4: Custom Implementation (Full Control)
**Use when:**
- Unique auth requirements
- Cost optimization at scale
- Regulatory compliance
- Legacy integration

**Tool:** Lucia or Custom

```typescript
// Custom with Lucia
import { Lucia } from 'lucia'
import { PrismaAdapter } from '@lucia-auth/adapter-prisma'

const adapter = new PrismaAdapter(prisma.session, prisma.user)
export const lucia = new Lucia(adapter, {
  sessionCookie: {
    attributes: {
      secure: process.env.NODE_ENV === 'production'
    }
  }
})
```

## Quick Decision Matrix

| Requirement | Auth.js | Clerk | Lucia | Custom |
|-------------|---------|-------|-------|--------|
| Setup time | Medium | Fast | Medium | Slow |
| OAuth providers | ✅ | ✅ | Manual | Manual |
| Pre-built UI | ❌ | ✅ | ❌ | ❌ |
| User management | ❌ | ✅ | ❌ | Build |
| Organizations | ❌ | ✅ | ❌ | Build |
| Self-hosted | ✅ | ❌ | ✅ | ✅ |
| Cost at scale | Free | $$$ | Free | Varies |
| Customization | High | Medium | High | Full |
| Type safety | Good | Good | Best | Varies |

## Security Checklist

Regardless of solution chosen:

- [ ] HTTPS only (no HTTP fallback)
- [ ] HttpOnly cookies for sessions
- [ ] CSRF protection enabled
- [ ] Secure password hashing (Argon2 or bcrypt)
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts
- [ ] Secure session invalidation
- [ ] Audit logging for auth events

## Token Strategy

### Session-based (Recommended for web)
```
Pros:
• Server controls invalidation
• No token storage client-side
• Smaller payload

Cons:
• Requires session store
• Sticky sessions for scaling
```

### JWT-based (For APIs/SPAs)
```
Pros:
• Stateless
• Works across services
• Mobile-friendly

Cons:
• Can't invalidate easily
• Token size
• Key rotation complexity
```

### Hybrid (Best of both)
```
• Short-lived access tokens (15 min)
• Refresh tokens in HttpOnly cookies
• Server-side refresh token rotation
• Can revoke via refresh token blacklist
```

## Default Recommendation

**For most Next.js applications:** Auth.js v5

```
Rationale:
• Official Next.js integration
• 50+ OAuth providers
• Session or JWT modes
• Active development
• Large community
• Free and open source
```

---

**Framework Version:** 1.0
**Used By:** appgen (auth implementation phase)
