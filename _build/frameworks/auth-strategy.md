# Progressive Auth Strategy Framework

Decision framework for selecting authentication approach based on project requirements. Used when knowledge base has no explicit preference.

## Decision Tree

```
START: What type of auth do you need?
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

### Level 1: Session-Only (Simplest)
**Use when:**
- Internal tools
- Prototype/MVP
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
