---
name: project-scaffold
description: Setup scripts for React+Vite, Astro, and Next.js projects with design system integration
---

# Project Scaffold Skill

**Type:** Reference Skill
**Purpose:** Provide setup scripts for React+Vite, Astro, and Next.js projects

## Overview

This skill provides executable setup scripts for the three supported tech stacks. Each script:
- Creates the project with the official CLI
- Configures Tailwind with our design system
- Adds the component utility classes
- Initializes git with an initial commit

## Setup Scripts

Located in `scripts/`:

| Script | Stack | Usage |
|--------|-------|-------|
| `setup-vite.sh` | React + Vite + Tailwind | `./setup-vite.sh my-project` |
| `setup-next.sh` | Next.js + Tailwind | `./setup-next.sh my-project` |
| `setup-astro.sh` | Astro + React + Tailwind | `./setup-astro.sh my-project` |

### Usage

```bash
# From the plugin scripts directory
~/.claude/plugins/local-plugins/webgen/skills/project-scaffold/scripts/setup-vite.sh my-landing-page

# Or reference the full path
${CLAUDE_PLUGIN_ROOT}/skills/project-scaffold/scripts/setup-vite.sh my-landing-page
```

## Stack Selection Guide

| Need | Recommendation | Script |
|------|---------------|--------|
| Simple landing page | React + Vite | `setup-vite.sh` |
| Portfolio, marketing | React + Vite | `setup-vite.sh` |
| Blog, documentation | Astro | `setup-astro.sh` |
| Content-heavy site | Astro | `setup-astro.sh` |
| App with API routes | Next.js | `setup-next.sh` |
| Dynamic content/auth | Next.js | `setup-next.sh` |
| E-commerce | Next.js | `setup-next.sh` |

## What Each Script Does

### setup-vite.sh

1. `pnpm create vite@latest` with react-ts template
2. Adds tailwindcss, postcss, autoprefixer, lucide-react
3. Creates tailwind.config.js with design system colors
4. Creates index.css with CSS variables and component classes
5. Creates src/components directory
6. Creates CHANGELOG.md
7. `git init` + initial commit

### setup-next.sh

1. `pnpm create next-app@latest` with TypeScript, Tailwind, App Router
2. Adds lucide-react
3. Updates tailwind.config.ts with design system colors
4. Updates globals.css with CSS variables and component classes
5. Creates src/components directory
6. Creates CHANGELOG.md
7. Amends initial commit

### setup-astro.sh

1. `pnpm create astro@latest` with minimal template
2. Adds @astrojs/tailwind, @astrojs/react, lucide-react
3. Creates tailwind.config.mjs with design system colors
4. Creates src/styles/globals.css with CSS variables and classes
5. Creates src/layouts/Layout.astro base layout
6. Creates CHANGELOG.md
7. `git init` + initial commit

## Folder Structures Created

### React + Vite
```
project-name/
├── public/
├── src/
│   ├── components/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── vite.config.ts
├── CHANGELOG.md
└── .gitignore
```

### Next.js (App Router)
```
project-name/
├── public/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   └── components/
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.js
├── CHANGELOG.md
└── .gitignore
```

### Astro
```
project-name/
├── public/
├── src/
│   ├── components/
│   ├── layouts/
│   │   └── Layout.astro
│   ├── pages/
│   │   └── index.astro
│   └── styles/
│       └── globals.css
├── package.json
├── tailwind.config.mjs
├── astro.config.mjs
├── tsconfig.json
├── CHANGELOG.md
└── .gitignore
```

## Dev Server Ports

After running setup:

```bash
cd project-name
pnpm dev
```

| Stack | Port |
|-------|------|
| Vite | http://localhost:5173 |
| Next.js | http://localhost:3000 |
| Astro | http://localhost:4321 |

## Design System Included

All scripts inject the same design system:

### CSS Variables
- `--primary`: Deep indigo (243 75% 59%)
- `--secondary`: Soft gray (240 5% 96%)
- `--accent`: Warm amber (35 92% 60%)
- Full dark mode variants

### Component Classes
- Buttons: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-outline`
- Cards: `.card`, `.feature-card`, `.pricing-card`, `.testimonial-card`
- Layout: `.nav`, `.hero`, `.section`, `.cta`, `.footer`
- Grid: `.grid-features`, `.grid-cards`

## Customizing Scripts

Edit the scripts to:
- Change default dependencies
- Add additional setup steps
- Modify the design system
- Add project-specific configuration

Scripts are version-controlled, so changes are tracked.
