# Progressive Framework Selection Framework

Decision framework for selecting web frameworks based on project requirements. Used when knowledge base has no explicit preference.

## Decision Tree

```
START: What are you building?
│
├─► Full-stack web app → Next.js or Remix
│   │
│   ├─► Content-heavy, SEO critical → Next.js (App Router)
│   │   • Marketing sites with dynamic content
│   │   • E-commerce
│   │   • Blogs with auth
│   │
│   ├─► Complex forms, mutations → Remix
│   │   • Multi-step workflows
│   │   • Heavy CRUD operations
│   │   • Progressive enhancement priority
│   │
│   └─► Real-time, collaborative → Next.js + Socket.io/Liveblocks
│       • Chat applications
│       • Collaborative editing
│       • Live dashboards
│
├─► Static/content site → Astro
│   │
│   ├─► Documentation → Astro + Starlight
│   ├─► Blog → Astro + MDX
│   └─► Marketing → Astro (islands for interactivity)
│
├─► Single-page app (SPA) → Vite + React/Vue/Svelte
│   │
│   ├─► Dashboard/admin → Vite + React + TanStack
│   ├─► Internal tools → Vite + React
│   └─► Embeddable widget → Vite + Preact/Svelte
│
└─► API only → Hono / Fastify / Express
    • Microservices
    • Backend for mobile app
    • Serverless functions
```

## Progressive Complexity Scale

### Level 1: Static Site (Simplest)
**Use when:**
- Content rarely changes
- No user authentication
- SEO is primary concern
- Budget-conscious hosting

**Tool:** Astro

```bash
npm create astro@latest
```

**Upgrade trigger:** Need dynamic content, user accounts, real-time features

---

### Level 2: Jamstack (Static + API)
**Use when:**
- Mostly static with some dynamic
- Third-party services for dynamic features
- Want CDN edge performance

**Tool:** Astro + External APIs

**Upgrade trigger:** Complex server logic, database needs, custom auth

---

### Level 3: Full-Stack Framework (Production Standard)
**Use when:**
- User authentication required
- Database-backed features
- Server-side rendering needed
- Complex business logic

**Tool:** Next.js (App Router)

```bash
npx create-next-app@latest --typescript --tailwind --eslint
```

**Upgrade trigger:** Extreme scale, microservices architecture, specific runtime needs

---

### Level 4: Custom Architecture (Scale)
**Use when:**
- Microservices required
- Multiple teams
- Polyglot services
- Extreme performance needs

**Tools:** Multiple services, API gateway, container orchestration

## Quick Decision Matrix

| Requirement | Next.js | Remix | Astro | Vite SPA |
|-------------|---------|-------|-------|----------|
| SSR | ✅ | ✅ | ✅ | ❌ |
| SSG | ✅ | ❌ | ✅ | ❌ |
| RSC | ✅ | ❌ | ❌ | ❌ |
| Forms | Good | Best | Basic | Manual |
| SEO | ✅ | ✅ | ✅ | ❌ |
| Bundle size | Medium | Medium | Smallest | Small |
| Learning curve | Medium | Medium | Low | Low |
| Deployment | Easy | Easy | Easiest | Easy |
| Real-time | Plugin | Plugin | Plugin | Manual |
| Edge runtime | ✅ | ✅ | ✅ | N/A |

## Framework-Specific Strengths

### Next.js 14+ (App Router)
```
Best for:
• React Server Components (RSC)
• Streaming SSR
• Incremental Static Regeneration
• Vercel deployment
• Large ecosystem

Avoid if:
• Need progressive enhancement
• Bundle size is critical
• Prefer simpler mental model
```

### Remix
```
Best for:
• Form-heavy applications
• Progressive enhancement
• Nested routing with data
• Error boundaries
• Web standards focus

Avoid if:
• Heavy static content
• Need ISR/SSG
• Team knows Next.js well
```

### Astro
```
Best for:
• Content sites
• Documentation
• Minimal JavaScript
• Multi-framework islands
• Maximum performance

Avoid if:
• Complex client interactivity
• Real-time features
• Heavy state management
```

### Vite + React
```
Best for:
• Admin dashboards
• Internal tools
• Embedded widgets
• Maximum flexibility

Avoid if:
• SEO is important
• Need SSR
• Want conventions/structure
```

## Hosting Recommendations

| Framework | Recommended Host | Alternative |
|-----------|------------------|-------------|
| Next.js | Vercel | Netlify, Railway |
| Remix | Fly.io | Vercel, Railway |
| Astro | Netlify | Vercel, Cloudflare |
| Vite SPA | Netlify | Vercel, S3+CloudFront |

## Default Recommendation

**For most web applications:** Next.js 14+ with App Router

```
Rationale:
• Largest ecosystem and community
• Excellent documentation
• Easy deployment (Vercel)
• Covers 90% of use cases
• Good performance defaults
• TypeScript-first
```

---

**Framework Version:** 1.0
**Used By:** appgen, webgen (framework selection phase)
