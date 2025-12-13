# shadcn/ui Inspired Patterns

Reference patterns based on shadcn/ui design principles.

## Philosophy

1. **Composable** - Small, focused components that combine well
2. **Customizable** - CSS variables for easy theming
3. **Accessible** - Built with a11y in mind
4. **Consistent** - Unified visual language

## Complete Component Examples

### Navigation with Mobile Menu

```tsx
import { useState } from 'react';
import { Menu, X } from 'lucide-react';

export function Navigation() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="nav">
      <div className="nav-container">
        <a href="/" className="nav-logo">Brand</a>

        {/* Desktop Nav */}
        <div className="nav-links">
          <a href="#features" className="nav-link">Features</a>
          <a href="#pricing" className="nav-link">Pricing</a>
          <a href="#about" className="nav-link">About</a>
          <button className="btn btn-primary btn-sm">Get Started</button>
        </div>

        {/* Mobile Toggle */}
        <button
          className="md:hidden"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden border-t">
          <div className="container py-4 space-y-4">
            <a href="#features" className="block nav-link">Features</a>
            <a href="#pricing" className="block nav-link">Pricing</a>
            <a href="#about" className="block nav-link">About</a>
            <button className="btn btn-primary w-full">Get Started</button>
          </div>
        </div>
      )}
    </nav>
  );
}
```

### Hero with Background Pattern

```tsx
export function Hero() {
  return (
    <section className="hero relative">
      {/* Optional background pattern */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] opacity-50" />

      <div className="hero-container">
        <span className="inline-block px-4 py-1.5 mb-6 text-sm font-medium bg-primary/10 text-primary rounded-full">
          Now in Beta
        </span>

        <h1 className="hero-title">
          Build faster with
          <span className="text-primary"> modern tools</span>
        </h1>

        <p className="hero-subtitle">
          Create beautiful, responsive websites in minutes.
          No design skills required.
        </p>

        <div className="hero-actions">
          <button className="btn btn-primary btn-lg">
            Start Building
            <ArrowRight className="ml-2 h-4 w-4" />
          </button>
          <button className="btn btn-outline btn-lg">
            View Demo
          </button>
        </div>
      </div>
    </section>
  );
}
```

### Feature Grid

```tsx
import { Zap, Shield, Sparkles } from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Optimized for speed with automatic code splitting and lazy loading."
  },
  {
    icon: Shield,
    title: "Secure by Default",
    description: "Built-in security features protect your site and users."
  },
  {
    icon: Sparkles,
    title: "Beautiful Design",
    description: "Pre-built components that look great out of the box."
  }
];

export function Features() {
  return (
    <section className="section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Everything you need</h2>
          <p className="section-subtitle">
            Powerful features to help you build amazing websites.
          </p>
        </div>

        <div className="grid-features">
          {features.map((feature) => (
            <div key={feature.title} className="feature-card">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### Pricing Cards

```tsx
import { Check } from 'lucide-react';

const plans = [
  {
    name: "Starter",
    price: "$9",
    description: "Perfect for side projects",
    features: ["5 projects", "Basic analytics", "Email support"],
  },
  {
    name: "Pro",
    price: "$29",
    description: "For growing businesses",
    features: ["Unlimited projects", "Advanced analytics", "Priority support", "Custom domains"],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "$99",
    description: "For large teams",
    features: ["Everything in Pro", "SSO", "Dedicated support", "SLA"],
  },
];

export function Pricing() {
  return (
    <section className="section bg-muted/50">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Simple Pricing</h2>
          <p className="section-subtitle">
            Choose the plan that works for you.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`pricing-card ${
                plan.popular ? 'border-primary ring-2 ring-primary' : ''
              }`}
            >
              {plan.popular && (
                <span className="inline-block px-3 py-1 text-xs font-medium bg-primary text-primary-foreground rounded-full mb-4">
                  Most Popular
                </span>
              )}

              <h3 className="text-xl font-bold">{plan.name}</h3>
              <p className="text-muted-foreground text-sm mt-1">{plan.description}</p>

              <div className="my-6">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-muted-foreground">/month</span>
              </div>

              <ul className="space-y-3 text-left mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                className={`btn w-full ${
                  plan.popular ? 'btn-primary' : 'btn-outline'
                }`}
              >
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### Testimonial Section

```tsx
const testimonials = [
  {
    quote: "This tool has completely transformed how we build websites. Highly recommended!",
    author: "Sarah Johnson",
    role: "Lead Developer",
    company: "TechCorp",
  },
  {
    quote: "The design system is beautiful and the components are so easy to customize.",
    author: "Mike Chen",
    role: "Designer",
    company: "Creative Studio",
  },
  {
    quote: "We shipped our new site in half the time. The quality is incredible.",
    author: "Emily Davis",
    role: "Product Manager",
    company: "StartupXYZ",
  },
];

export function Testimonials() {
  return (
    <section className="section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Loved by developers</h2>
          <p className="section-subtitle">
            See what others are saying about us.
          </p>
        </div>

        <div className="grid-features">
          {testimonials.map((t) => (
            <div key={t.author} className="testimonial-card">
              <p className="text-lg mb-6">"{t.quote}"</p>
              <div className="not-italic">
                <p className="font-semibold">{t.author}</p>
                <p className="text-sm text-muted-foreground">
                  {t.role}, {t.company}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### CTA Section

```tsx
export function CTA() {
  return (
    <section className="cta">
      <div className="cta-container">
        <h2 className="cta-title">Ready to get started?</h2>
        <p className="cta-subtitle">
          Join thousands of developers building amazing websites.
        </p>
        <div className="cta-actions">
          <button className="btn btn-lg bg-white text-primary hover:bg-white/90">
            Start Free Trial
          </button>
          <button className="btn btn-lg border-white/30 text-white hover:bg-white/10">
            Contact Sales
          </button>
        </div>
      </div>
    </section>
  );
}
```

### Footer

```tsx
export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-section">
          <h3 className="footer-title">Brand</h3>
          <p className="text-sm text-muted-foreground">
            Building the future of web development.
          </p>
        </div>

        <div className="footer-section">
          <h4 className="footer-title">Product</h4>
          <div className="footer-links">
            <a href="#" className="footer-link block">Features</a>
            <a href="#" className="footer-link block">Pricing</a>
            <a href="#" className="footer-link block">Changelog</a>
          </div>
        </div>

        <div className="footer-section">
          <h4 className="footer-title">Company</h4>
          <div className="footer-links">
            <a href="#" className="footer-link block">About</a>
            <a href="#" className="footer-link block">Blog</a>
            <a href="#" className="footer-link block">Careers</a>
          </div>
        </div>

        <div className="footer-section">
          <h4 className="footer-title">Legal</h4>
          <div className="footer-links">
            <a href="#" className="footer-link block">Privacy</a>
            <a href="#" className="footer-link block">Terms</a>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; 2024 Brand. All rights reserved.</p>
      </div>
    </footer>
  );
}
```

## Industry-Specific Patterns

### Restaurant

```tsx
// Menu Item Card
<div className="card p-4 flex gap-4">
  <img src={item.image} alt={item.name} className="w-24 h-24 rounded-lg object-cover" />
  <div className="flex-1">
    <div className="flex justify-between items-start">
      <h3 className="font-semibold">{item.name}</h3>
      <span className="text-primary font-bold">${item.price}</span>
    </div>
    <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
  </div>
</div>

// Reservation CTA
<section className="cta bg-amber-700">
  <div className="cta-container">
    <h2 className="cta-title">Reserve Your Table</h2>
    <p className="cta-subtitle">Experience exceptional dining</p>
    <button className="btn btn-lg bg-white text-amber-700">
      Make Reservation
    </button>
  </div>
</section>
```

### Portfolio

```tsx
// Project Card with Hover
<div className="group relative overflow-hidden rounded-lg">
  <img
    src={project.image}
    alt={project.title}
    className="w-full aspect-video object-cover transition-transform group-hover:scale-105"
  />
  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
    <div className="text-center text-white p-4">
      <h3 className="text-xl font-bold">{project.title}</h3>
      <p className="text-sm mt-2">{project.category}</p>
      <button className="btn btn-outline border-white text-white mt-4">
        View Project
      </button>
    </div>
  </div>
</div>
```

### SaaS Dashboard

```tsx
// Stats Card
<div className="card p-6">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-sm text-muted-foreground">Total Revenue</p>
      <p className="text-2xl font-bold mt-1">$45,231.89</p>
      <p className="text-xs text-green-600 mt-1">+20.1% from last month</p>
    </div>
    <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
      <DollarSign className="h-6 w-6 text-primary" />
    </div>
  </div>
</div>
```

## Animation Patterns

```css
/* Subtle entrance */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* Staggered children */
.stagger-children > * {
  animation: fadeIn 0.5s ease-out backwards;
}
.stagger-children > *:nth-child(1) { animation-delay: 0ms; }
.stagger-children > *:nth-child(2) { animation-delay: 100ms; }
.stagger-children > *:nth-child(3) { animation-delay: 200ms; }
```

## Icon Usage

Use [Lucide React](https://lucide.dev/) for icons:

```tsx
import { ArrowRight, Check, Menu, X, Zap, Shield, Sparkles } from 'lucide-react';

// Usage
<ArrowRight className="h-4 w-4" />
```

Common icons by purpose:
- Navigation: `Menu`, `X`, `ChevronDown`
- Actions: `ArrowRight`, `Plus`, `Edit`, `Trash`
- Status: `Check`, `AlertCircle`, `Info`
- Features: `Zap`, `Shield`, `Sparkles`, `Globe`
- Social: `Github`, `Twitter`, `Linkedin`
