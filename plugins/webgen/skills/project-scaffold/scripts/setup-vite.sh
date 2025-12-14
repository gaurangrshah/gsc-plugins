#!/bin/bash
# Setup React + Vite + Tailwind project
# Usage: ./setup-vite.sh <project-name>

set -e

PROJECT_NAME="${1:-my-app}"

echo "Creating React + Vite project: $PROJECT_NAME"

# Create project with Vite
pnpm create vite@latest "$PROJECT_NAME" --template react-ts

cd "$PROJECT_NAME"

# Setup local node_modules for NAS performance
LOCAL_NM="$HOME/.local/node_modules/$PROJECT_NAME"
mkdir -p "$LOCAL_NM"
rm -rf node_modules 2>/dev/null
ln -s "$LOCAL_NM" node_modules
echo "✓ node_modules → $LOCAL_NM"

# Install Tailwind and dependencies
pnpm add -D tailwindcss postcss autoprefixer
pnpm add lucide-react

# Initialize Tailwind
pnpm tailwindcss init -p

# Update tailwind.config.js with our design system
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
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
  plugins: [],
}
EOF

# Create globals.css with design system
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 4%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 4%;
    --primary: 243 75% 59%;
    --primary-foreground: 0 0% 100%;
    --secondary: 240 5% 96%;
    --secondary-foreground: 240 6% 10%;
    --muted: 240 5% 96%;
    --muted-foreground: 240 4% 46%;
    --accent: 35 92% 60%;
    --accent-foreground: 35 92% 10%;
    --border: 240 6% 90%;
    --input: 240 6% 90%;
    --ring: 243 75% 59%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 240 10% 4%;
    --foreground: 0 0% 98%;
    --card: 240 6% 10%;
    --card-foreground: 0 0% 98%;
    --primary: 243 75% 70%;
    --secondary: 240 4% 16%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 4% 16%;
    --muted-foreground: 240 5% 65%;
    --border: 240 4% 16%;
    --input: 240 4% 16%;
  }

  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground;
  }
}

@layer components {
  .container {
    @apply mx-auto max-w-7xl px-4 sm:px-6 lg:px-8;
  }

  /* Buttons */
  .btn {
    @apply inline-flex items-center justify-center rounded-md text-sm font-medium
           transition-colors focus-visible:outline-none focus-visible:ring-2
           focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50;
  }
  .btn-primary { @apply bg-primary text-primary-foreground hover:bg-primary/90; }
  .btn-secondary { @apply bg-secondary text-secondary-foreground hover:bg-secondary/80; }
  .btn-outline { @apply border border-input bg-background hover:bg-accent hover:text-accent-foreground; }
  .btn-ghost { @apply hover:bg-accent hover:text-accent-foreground; }
  .btn-sm { @apply h-9 px-3; }
  .btn-md { @apply h-10 px-4 py-2; }
  .btn-lg { @apply h-11 px-8; }

  /* Cards */
  .card { @apply rounded-lg border bg-card text-card-foreground shadow-sm; }
  .feature-card { @apply rounded-lg border bg-card text-card-foreground shadow-sm p-6 hover:shadow-md transition-shadow; }
  .pricing-card { @apply rounded-lg border bg-card text-card-foreground shadow-sm p-8 text-center; }
  .testimonial-card { @apply rounded-lg border bg-card text-card-foreground shadow-sm p-6 italic; }

  /* Navigation */
  .nav { @apply sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur; }
  .nav-container { @apply container flex h-16 items-center justify-between; }
  .nav-logo { @apply text-xl font-bold; }
  .nav-links { @apply hidden md:flex items-center space-x-6; }
  .nav-link { @apply text-sm font-medium text-muted-foreground hover:text-foreground transition-colors; }

  /* Hero */
  .hero { @apply relative py-20 md:py-32 overflow-hidden; }
  .hero-container { @apply container flex flex-col items-center text-center; }
  .hero-title { @apply text-4xl md:text-6xl font-bold tracking-tight; }
  .hero-subtitle { @apply mt-6 text-xl text-muted-foreground max-w-2xl; }
  .hero-actions { @apply mt-10 flex flex-col sm:flex-row gap-4; }

  /* Sections */
  .section { @apply py-16 md:py-24; }
  .section-header { @apply text-center mb-12; }
  .section-title { @apply text-3xl md:text-4xl font-bold; }
  .section-subtitle { @apply mt-4 text-lg text-muted-foreground max-w-2xl mx-auto; }

  /* CTA */
  .cta { @apply py-16 md:py-24 bg-primary text-primary-foreground; }
  .cta-container { @apply container text-center; }
  .cta-title { @apply text-3xl md:text-4xl font-bold; }
  .cta-subtitle { @apply mt-4 text-lg opacity-90 max-w-2xl mx-auto; }
  .cta-actions { @apply mt-8 flex flex-col sm:flex-row gap-4 justify-center; }

  /* Footer */
  .footer { @apply border-t bg-muted/50 py-12; }
  .footer-container { @apply container grid gap-8 md:grid-cols-4; }
  .footer-section { @apply space-y-4; }
  .footer-title { @apply font-semibold; }
  .footer-links { @apply space-y-2 text-sm text-muted-foreground; }
  .footer-link { @apply hover:text-foreground transition-colors; }
  .footer-bottom { @apply container mt-8 pt-8 border-t text-center text-sm text-muted-foreground; }

  /* Grid layouts */
  .grid-features { @apply grid gap-8 md:grid-cols-2 lg:grid-cols-3; }
  .grid-cards { @apply grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4; }
}
EOF

# Create components directory
mkdir -p src/components

# Create CHANGELOG
cat > CHANGELOG.md << 'EOF'
# Changelog

## [0.1.0] - $(date +%Y-%m-%d)

### Added
- Initial project scaffold with React + Vite + Tailwind
- Design system with CSS variables
- Component utility classes
EOF

# Initialize git
git init
git add -A
git commit -m "chore: initial scaffold with React + Vite + Tailwind"

echo ""
echo "Project created successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  pnpm dev"
echo ""
