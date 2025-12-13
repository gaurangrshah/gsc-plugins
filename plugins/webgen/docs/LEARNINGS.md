# WebGen Learnings

Documented observations from test runs to inform future improvements.

## Test Session: 2024-12-13

### Projects Generated
1. **Fintech Landing (Elevate Wealth)** - Static HTML/CSS/JS
2. **Clarity Health** - Next.js + Tailwind (multiple attempts)

---

## Key Findings

### 1. Quality Degradation Pattern

**Observation:** Hero sections are strong and detailed, but quality noticeably degrades toward the footer.

| Section | Quality Level | Notes |
|---------|--------------|-------|
| Hero | High | Best attention, fresh research applied |
| Features | Good | Still detailed |
| Testimonials/Trust | Medium | Starting to see shortcuts |
| Pricing/CTA | Lower | Less polish |
| Footer | Lowest | Minimal effort, placeholder-ish |

**Root Cause:** LLM attention/effort naturally front-loads to beginning of generation.

**Solution (v1.3):** Anti-degradation protocol with:
- Equal effort mandate per section
- Quality checkpoints before proceeding
- Optional reverse-order generation
- Two-pass approach for complex pages

---

### 2. Infrastructure Issues on Network Filesystem

**Observation:** pnpm install extremely slow and prone to stalling on SMB/CIFS mounts.

**Symptoms:**
- Install stalls at 372/374 packages
- Multiple competing pnpm processes cause lock contention
- rm -rf node_modules takes minutes (thousands of files over network)
- Cross-volume pnpm store falls back to copy instead of hardlink

**Environment:**
- Project path: `/home/gs/workspace/` = CIFS mount to NAS
- pnpm store: Different volume

**Solution (v1.3):**
- Fail-fast infrastructure verification
- Network filesystem warning
- Install timeout with graceful fallback
- `--prefer-offline` flag

**Future consideration:** Move active development to local disk, sync to NAS.

---

### 3. Install Loop Bug

**Observation:** Agent would retry `rm -rf node_modules && pnpm install` indefinitely when install failed.

**Root Cause:** No timeout, no failure detection, just retry on any error.

**Solution (v1.3):**
- Install timeout (2 min max)
- Specific error reporting
- Escalate to user instead of infinite loop
- Option 3 fallback: try dev anyway with partial install

---

### 4. Duplicate Project Creation

**Observation:** Two folders created for same project:
- `clarity-health`
- `clarity-health - webgen`

**Root Cause:** No check for existing project before scaffolding.

**Solution (v1.3):** Check for existing `{slug}` or `{slug} - webgen` before creating.

---

### 5. Static vs React/Next.js Selection

**Observation:** Fintech used static HTML (single commit, 3 files). Clarity Health used Next.js (complex setup, install issues).

**Question:** When is static HTML the right choice vs full React stack?

| Static HTML | React/Next.js |
|-------------|---------------|
| Single page, no interactivity | Multi-page, dynamic content |
| No build step needed | Complex state management |
| Instant preview | Hot reload development |
| Simpler deployment | SSR/SSG capabilities |
| ~60KB total | ~200KB+ bundle |

**Recommendation:** Default to static HTML for simple landing pages. Use React only when:
- Multiple pages with shared components
- Complex interactivity (forms, dashboards)
- Server-side rendering needed
- API routes required

---

### 6. Research Capture

**v1.0:** No research captured (ephemeral in session)
**v1.1+:** Research saved to `research/competitive-analysis.md`

**Verified working:** Clarity Health had 166 lines of competitive research (One Medical, Oscar Health, Ro Health).

---

## Implemented in v1.3

| Issue | Solution | Status |
|-------|----------|--------|
| Monolithic commits | Section-by-section commit protocol | ✅ Added |
| Quality degradation | Anti-degradation protocol with checkpoints | ✅ Added |
| Accessibility gaps | Expanded WCAG checklist per component | ✅ Added |
| Install loops | Timeout + escalation | ✅ Added |
| Duplicate projects | Existence check before scaffold | ✅ Added |
| Network FS issues | Warning + --prefer-offline | ✅ Added |

## Implemented in v1.4

| Issue | Solution | Status |
|-------|----------|--------|
| Missing legal pages | Phase 4.5: Legal Pages conditional phase | ✅ Added |
| Placeholder legal links | Industry-specific templates generated | ✅ Added |
| No legal disclaimer | Mandatory disclaimer on all legal pages | ✅ Added |
| Generic legal content | Industry detection (fintech, healthcare, etc.) | ✅ Added |

## Recommendations for v1.5+

1. **Smarter stack selection** - Prefer static HTML for simple pages
2. **Local-first development** - Scaffold to local disk, not network mount
3. **Progressive quality gates** - Score each section 1-10 before proceeding
4. **Section-specific research** - Apply competitor insights per section, not just globally
5. **Preview verification** - Screenshot each section, not just final result
6. **Parallel generation** - Generate independent sections concurrently
7. **Code review integration** - Orchestrator dispatches reviewer after each major section
8. **Template library** - Save successful patterns for reuse
9. **Legal template library** - Pre-built legal templates per industry for faster generation

---

## Metrics to Track

- Time to first preview (scaffold → dev server running)
- Install success rate (complete vs partial vs failed)
- Quality consistency score (hero quality vs footer quality)
- User satisfaction per section
- Rework rate (how often user asks to redo a section)
