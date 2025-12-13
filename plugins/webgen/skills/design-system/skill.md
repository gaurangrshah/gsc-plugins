# Design System Skill

**Type:** Reference Skill
**Purpose:** Provide consistent, modern styling patterns for generated websites

## Overview

This skill provides a shadcn-inspired design system with CSS variables, component classes, and responsive patterns. Use this as the foundation for all generated components.

## Usage

When generating components, reference:
1. Color tokens via CSS variables
2. Component classes for consistent styling
3. Responsive patterns for mobile-first design
4. Dark mode support via `.dark` class

## Core Design Tokens

### Colors (HSL Format)

```css
:root {
  /* Primary - Deep indigo */
  --primary: 243 75% 59%;
  --primary-foreground: 0 0% 100%;

  /* Secondary - Soft gray */
  --secondary: 240 5% 96%;
  --secondary-foreground: 240 6% 10%;

  /* Accent - Warm amber */
  --accent: 35 92% 60%;
  --accent-foreground: 35 92% 10%;

  /* Background & Foreground */
  --background: 0 0% 100%;
  --foreground: 240 10% 4%;

  /* Muted */
  --muted: 240 5% 96%;
  --muted-foreground: 240 4% 46%;

  /* Card */
  --card: 0 0% 100%;
  --card-foreground: 240 10% 4%;

  /* Border & Input */
  --border: 240 6% 90%;
  --input: 240 6% 90%;
  --ring: 243 75% 59%;

  /* Radius */
  --radius: 0.5rem;
}

.dark {
  --primary: 243 75% 70%;
  --primary-foreground: 0 0% 100%;
  --secondary: 240 4% 16%;
  --secondary-foreground: 0 0% 98%;
  --accent: 35 92% 50%;
  --background: 240 10% 4%;
  --foreground: 0 0% 98%;
  --muted: 240 4% 16%;
  --muted-foreground: 240 5% 65%;
  --card: 240 6% 10%;
  --card-foreground: 0 0% 98%;
  --border: 240 4% 16%;
  --input: 240 4% 16%;
}
```

## Component Classes

### Buttons

```css
.btn {
  @apply inline-flex items-center justify-center rounded-md text-sm font-medium
         transition-colors focus-visible:outline-none focus-visible:ring-2
         focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50;
}

.btn-primary {
  @apply bg-primary text-primary-foreground hover:bg-primary/90;
}

.btn-secondary {
  @apply bg-secondary text-secondary-foreground hover:bg-secondary/80;
}

.btn-outline {
  @apply border border-input bg-background hover:bg-accent hover:text-accent-foreground;
}

.btn-ghost {
  @apply hover:bg-accent hover:text-accent-foreground;
}

/* Sizes */
.btn-sm { @apply h-9 px-3; }
.btn-md { @apply h-10 px-4 py-2; }
.btn-lg { @apply h-11 px-8; }
```

### Cards

```css
.card {
  @apply rounded-lg border bg-card text-card-foreground shadow-sm;
}

.card-header {
  @apply flex flex-col space-y-1.5 p-6;
}

.card-content {
  @apply p-6 pt-0;
}

.card-footer {
  @apply flex items-center p-6 pt-0;
}

/* Variants */
.feature-card {
  @apply card p-6 hover:shadow-md transition-shadow;
}

.pricing-card {
  @apply card p-8 text-center;
}

.testimonial-card {
  @apply card p-6 italic;
}
```

### Navigation

```css
.nav {
  @apply sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur;
}

.nav-container {
  @apply container flex h-16 items-center justify-between;
}

.nav-logo {
  @apply text-xl font-bold;
}

.nav-links {
  @apply hidden md:flex items-center space-x-6;
}

.nav-link {
  @apply text-sm font-medium text-muted-foreground hover:text-foreground transition-colors;
}

.nav-link-active {
  @apply text-foreground;
}
```

### Hero Sections

```css
.hero {
  @apply relative py-20 md:py-32 overflow-hidden;
}

.hero-container {
  @apply container flex flex-col items-center text-center;
}

.hero-title {
  @apply text-4xl md:text-6xl font-bold tracking-tight;
}

.hero-subtitle {
  @apply mt-6 text-xl text-muted-foreground max-w-2xl;
}

.hero-actions {
  @apply mt-10 flex flex-col sm:flex-row gap-4;
}
```

### Sections

```css
.section {
  @apply py-16 md:py-24;
}

.section-header {
  @apply text-center mb-12;
}

.section-title {
  @apply text-3xl md:text-4xl font-bold;
}

.section-subtitle {
  @apply mt-4 text-lg text-muted-foreground max-w-2xl mx-auto;
}
```

### Footer

```css
.footer {
  @apply border-t bg-muted/50 py-12;
}

.footer-container {
  @apply container grid gap-8 md:grid-cols-4;
}

.footer-section {
  @apply space-y-4;
}

.footer-title {
  @apply font-semibold;
}

.footer-links {
  @apply space-y-2 text-sm text-muted-foreground;
}

.footer-link {
  @apply hover:text-foreground transition-colors;
}

.footer-bottom {
  @apply container mt-8 pt-8 border-t text-center text-sm text-muted-foreground;
}
```

### CTA (Call to Action)

```css
.cta {
  @apply py-16 md:py-24 bg-primary text-primary-foreground;
}

.cta-container {
  @apply container text-center;
}

.cta-title {
  @apply text-3xl md:text-4xl font-bold;
}

.cta-subtitle {
  @apply mt-4 text-lg opacity-90 max-w-2xl mx-auto;
}

.cta-actions {
  @apply mt-8 flex flex-col sm:flex-row gap-4 justify-center;
}
```

## Responsive Patterns

### Container
```css
.container {
  @apply mx-auto max-w-7xl px-4 sm:px-6 lg:px-8;
}
```

### Grid Layouts
```css
/* 2 columns on md, 3 on lg */
.grid-features {
  @apply grid gap-8 md:grid-cols-2 lg:grid-cols-3;
}

/* 2 columns on sm, 3 on md, 4 on lg */
.grid-cards {
  @apply grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4;
}
```

### Typography Scale
```css
.text-display { @apply text-5xl md:text-7xl font-bold; }
.text-h1 { @apply text-4xl md:text-5xl font-bold; }
.text-h2 { @apply text-3xl md:text-4xl font-bold; }
.text-h3 { @apply text-2xl md:text-3xl font-semibold; }
.text-h4 { @apply text-xl md:text-2xl font-semibold; }
.text-body { @apply text-base; }
.text-small { @apply text-sm; }
```

## Usage Example

```tsx
export function Hero() {
  return (
    <section className="hero">
      <div className="hero-container">
        <h1 className="hero-title">
          Welcome to Our Site
        </h1>
        <p className="hero-subtitle">
          A compelling description of what we offer.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary btn-lg">
            Get Started
          </button>
          <button className="btn btn-outline btn-lg">
            Learn More
          </button>
        </div>
      </div>
    </section>
  );
}
```

## Tailwind Config Integration

Add to `tailwind.config.js`:

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
}
```

## References

See `references/shadcn.md` for detailed component patterns and examples.
