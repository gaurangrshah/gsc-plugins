---
title: Auth Integration Skill
type: skill
created: 2024-12-13
tags: [appgen, auth, authentication, jwt, nextauth]
---

# Auth Integration Skill

Provides guidance for integrating authentication into full-stack applications.

## Purpose

This skill helps the appgen agent integrate authentication providers (Auth.js, Clerk, Lucia) into applications.

---

## Authentication Options

### 1. Auth.js (NextAuth) - Next.js Apps

**Best for:** Next.js applications with email/password or OAuth

**Features:**
- Built-in OAuth providers (Google, GitHub, etc.)
- Email/password authentication
- Session management
- Database adapters (Prisma, Drizzle)

**Installation:**
```bash
npm install next-auth @auth/prisma-adapter
```

### 2. Clerk - Hosted Auth

**Best for:** Quick setup, modern UI, managed auth

**Features:**
- Hosted UI components
- OAuth providers
- User management dashboard
- Email verification
- Multi-factor authentication

**Installation:**
```bash
npm install @clerk/nextjs
```

### 3. Lucia - Lightweight Custom

**Best for:** API-only apps, full control, minimal dependencies

**Features:**
- Framework-agnostic
- Session-based or token-based
- Full control over auth flow
- Works with any database

**Installation:**
```bash
npm install lucia @lucia-auth/adapter-prisma
```

---

## Auth.js (NextAuth) Setup

### Step 1: Install Dependencies

```bash
npm install next-auth @auth/prisma-adapter
npm install bcryptjs
npm install -D @types/bcryptjs
```

### Step 2: Prisma Schema

```prisma
model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified DateTime?
  image         String?
  passwordHash  String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  accounts Account[]
  sessions Session[]

  @@index([email])
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@index([userId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}
```

### Step 3: Auth Configuration

Create `lib/auth.ts`:

```typescript
import { NextAuthOptions } from 'next-auth';
import { PrismaAdapter } from '@auth/prisma-adapter';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import { prisma } from '@/lib/db';
import bcrypt from 'bcryptjs';
import { z } from 'zod';

const credentialsSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Invalid credentials');
        }

        const { email, password } = credentialsSchema.parse(credentials);

        const user = await prisma.user.findUnique({
          where: { email },
        });

        if (!user || !user.passwordHash) {
          throw new Error('Invalid credentials');
        }

        const isValidPassword = await bcrypt.compare(
          password,
          user.passwordHash
        );

        if (!isValidPassword) {
          throw new Error('Invalid credentials');
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
        };
      },
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/login',
    signOut: '/logout',
    error: '/error',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
};
```

### Step 4: API Route

Create `app/api/auth/[...nextauth]/route.ts`:

```typescript
import NextAuth from 'next-auth';
import { authOptions } from '@/lib/auth';

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
```

### Step 5: Auth Provider

Create `components/providers/auth-provider.tsx`:

```typescript
'use client';

import { SessionProvider } from 'next-auth/react';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

Wrap app in `app/layout.tsx`:

```typescript
import { AuthProvider } from '@/components/providers/auth-provider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
```

### Step 6: Protected Routes

Create middleware (`middleware.ts`):

```typescript
import { withAuth } from 'next-auth/middleware';

export default withAuth({
  pages: {
    signIn: '/login',
  },
});

export const config = {
  matcher: ['/dashboard/:path*', '/api/users/:path*'],
};
```

### Step 7: Use in Components

```typescript
'use client';

import { useSession, signIn, signOut } from 'next-auth/react';

export function UserButton() {
  const { data: session, status } = useSession();

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  if (!session) {
    return <button onClick={() => signIn()}>Sign In</button>;
  }

  return (
    <div>
      <p>Signed in as {session.user.email}</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  );
}
```

### Step 8: Server-Side Auth

```typescript
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function GET() {
  const session = await getServerSession(authOptions);

  if (!session) {
    return new Response('Unauthorized', { status: 401 });
  }

  // Use session.user.id...
}
```

---

## Lucia Setup (API-Only)

### Step 1: Install Dependencies

```bash
npm install lucia @lucia-auth/adapter-prisma
npm install bcryptjs
npm install -D @types/bcryptjs
```

### Step 2: Prisma Schema

```prisma
model User {
  id           String    @id @default(cuid())
  email        String    @unique
  passwordHash String
  createdAt    DateTime  @default(now())
  updatedAt    DateTime  @updatedAt

  sessions Session[]

  @@index([email])
}

model Session {
  id        String   @id @default(cuid())
  userId    String
  expiresAt DateTime
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
}
```

### Step 3: Lucia Configuration

Create `lib/auth.ts`:

```typescript
import { Lucia } from 'lucia';
import { PrismaAdapter } from '@lucia-auth/adapter-prisma';
import { prisma } from './db';

const adapter = new PrismaAdapter(prisma.session, prisma.user);

export const lucia = new Lucia(adapter, {
  sessionCookie: {
    attributes: {
      secure: process.env.NODE_ENV === 'production',
    },
  },
  getUserAttributes: (attributes) => {
    return {
      email: attributes.email,
    };
  },
});

declare module 'lucia' {
  interface Register {
    Lucia: typeof lucia;
    DatabaseUserAttributes: {
      email: string;
    };
  }
}
```

### Step 4: Register Endpoint

```typescript
import { lucia } from '@/lib/auth';
import { prisma } from '@/lib/db';
import bcrypt from 'bcryptjs';
import { z } from 'zod';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

app.post('/api/auth/register', async (c) => {
  try {
    const body = await c.req.json();
    const { email, password } = registerSchema.parse(body);

    const passwordHash = await bcrypt.hash(password, 10);

    const user = await prisma.user.create({
      data: { email, passwordHash },
    });

    const session = await lucia.createSession(user.id, {});
    const sessionCookie = lucia.createSessionCookie(session.id);

    c.header('Set-Cookie', sessionCookie.serialize());

    return c.json({ data: { userId: user.id } }, 201);
  } catch (error) {
    // Handle errors...
  }
});
```

### Step 5: Login Endpoint

```typescript
app.post('/api/auth/login', async (c) => {
  try {
    const body = await c.req.json();
    const { email, password } = registerSchema.parse(body);

    const user = await prisma.user.findUnique({ where: { email } });

    if (!user) {
      return c.json({
        error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password' },
      }, 401);
    }

    const validPassword = await bcrypt.compare(password, user.passwordHash);

    if (!validPassword) {
      return c.json({
        error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password' },
      }, 401);
    }

    const session = await lucia.createSession(user.id, {});
    const sessionCookie = lucia.createSessionCookie(session.id);

    c.header('Set-Cookie', sessionCookie.serialize());

    return c.json({ data: { userId: user.id } });
  } catch (error) {
    // Handle errors...
  }
});
```

### Step 6: Auth Middleware

```typescript
import { lucia } from '@/lib/auth';

export async function authMiddleware(c: Context, next: Next) {
  const sessionId = getCookie(c, lucia.sessionCookieName);

  if (!sessionId) {
    return c.json({
      error: { code: 'UNAUTHORIZED', message: 'Authentication required' },
    }, 401);
  }

  const { session, user } = await lucia.validateSession(sessionId);

  if (!session) {
    return c.json({
      error: { code: 'INVALID_SESSION', message: 'Invalid or expired session' },
    }, 401);
  }

  c.set('user', user);
  c.set('session', session);

  await next();
}
```

---

## Environment Variables

Add to `.env.example`:

**Auth.js:**
```env
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-here"  # Generate with: openssl rand -base64 32

# OAuth (if using)
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

**Lucia:**
```env
# Session secret
SESSION_SECRET="your-secret-here"
```

---

## Security Checklist

- [ ] Passwords hashed with bcrypt (cost factor 10+)
- [ ] Session secrets in environment variables
- [ ] HTTPS enforced in production
- [ ] JWT secrets strong and random
- [ ] Password minimum length 8 characters
- [ ] Rate limiting on auth endpoints
- [ ] Email verification implemented (if needed)
- [ ] Session expiration configured
- [ ] Secure cookie flags set (httpOnly, secure, sameSite)

---

## Version History

**v1.0** (2024-12-13)
- Initial skill for appgen plugin
- Auth.js (NextAuth) setup guide
- Lucia setup guide
- Security best practices
