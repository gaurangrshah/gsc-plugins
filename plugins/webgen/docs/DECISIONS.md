# Architecture Decision Records

## ADR-001: Pivot from Local LLMs to Claude Code Plugin

**Date:** 2024-12-12
**Status:** Accepted

### Context

We built a 6-stage website generation pipeline using Ollama with local LLMs:
- **Researcher** - Web search for competitive analysis
- **Product Manager** - PRD generation with specific copy
- **Planner** - JSON spec with section/component structure
- **Coder** - Code generation from spec
- **Critic** - Quality review and scoring
- **Refiner** - Iteration based on feedback

Models used:
- Llama 3.1 (8B) - For planning/PRD (instruction-following)
- CodeLlama (13B) - For code generation

### Problem

Local LLMs failed in fundamental ways:

1. **JSON Reliability (~40% success)**
   - Llama 3.1 produced malformed JSON frequently
   - Trailing commas, unclosed braces, invalid escapes
   - Even with explicit JSON examples and repair logic

2. **Few-Shot Example Copying**
   - CodeLlama copied example content, not just format
   - A SaaS example produced SaaS output for restaurant prompts
   - Explicit framing ("FORMAT ONLY") was ignored

3. **Instruction Following**
   - "NEVER do X" instructions were ignored
   - Models hallucinated imports that don't exist
   - Generated Pages Router when shown App Router examples

### Decision

Pivot to a Claude Code plugin that uses the Max subscription:
- Claude reliably follows instructions
- No JSON parsing failures
- Proper code generation quality
- No additional API costs (uses existing subscription)

### Consequences

**Positive:**
- Reliable code generation
- Natural conversation for clarifying questions
- Leverages Claude's extensive training
- Zero marginal cost per generation

**Negative:**
- Requires Claude Code CLI (already have)
- No offline capability
- Dependent on Anthropic's service

### Alternatives Considered

1. **LangChain/LangGraph** - Rejected: orchestration doesn't fix model capability
2. **Fine-tuned local models** - Rejected: requires significant resources, still limited
3. **Hybrid (local + API fallback)** - Rejected: complexity without benefit
4. **Claude API directly** - Rejected: adds API costs when Max covers CLI usage

---

## ADR-002: Privacy-First PII Handling

**Date:** 2024-12-12
**Status:** Accepted

### Context

Websites often need contact information (address, phone, email). Users may hesitate to share this with AI systems.

### Decision

The agent NEVER asks for PII. For contact sections:
- **Address:** Fictional but realistic (123 Main Street, Anytown, ST 12345)
- **Phone:** 555-XXX-XXXX format (reserved for fiction)
- **Email:** contact@{business-slug}.example.com
- **Social:** "#" placeholder URLs

User adds real data locally after generation.

### Rationale

1. **Privacy by default** - No PII in conversation history
2. **Faster workflow** - Don't need to type out contact info
3. **Easily replaceable** - Find/replace in generated code
4. **Safe examples** - 555 numbers can't accidentally call someone

### Consequences

Generated code works immediately for preview. User updates placeholders before deployment.

---

## ADR-003: Default to React + Vite

**Date:** 2024-12-12
**Status:** Accepted

### Context

Need a default stack when server-side features aren't required.

### Decision

Default: React + Vite + Tailwind

| Need | Recommendation |
|------|---------------|
| Simple landing page | React + Vite |
| Content-heavy/blog | Astro |
| Server/API needed | Next.js |

### Rationale

1. **Fastest** - Vite's dev server is instant
2. **Simplest** - No SSR complexity to debug
3. **Familiar** - React is widely known
4. **Sufficient** - Most landing pages don't need SSR

### Alternatives

- **Next.js as default** - Rejected: overkill for static sites
- **Astro as default** - Considered: great for content, but React more universal
- **Plain HTML** - Rejected: limits component reuse

---

## ADR-004: Atomic Git Workflow

**Date:** 2024-12-12
**Status:** Accepted

### Context

Generated projects need version control for professional use.

### Decision

Every project gets:
1. `git init` immediately after scaffold
2. Atomic commits after each logical unit
3. Conventional commit messages (feat|fix|chore|docs)
4. CHANGELOG.md updated with features

### Commit Pattern

```
chore: initial scaffold
feat: add navigation component
feat: add hero section
feat: add features grid
feat: add testimonials section
feat: add CTA section
feat: add footer
docs: update changelog
```

### Rationale

1. **Easy rollback** - Can revert specific sections
2. **Clear history** - Understand what was added when
3. **Professional practice** - Real projects use git
4. **Iteration friendly** - Can branch for variations

---

## ADR-005: Embedded Design System

**Date:** 2024-12-12
**Status:** Accepted

### Context

Need consistent styling across generated components.

### Decision

Embed a shadcn-inspired design system with:
- CSS variables (HSL format) for theming
- Component classes (btn, card, nav, hero, etc.)
- Responsive utilities (container, grids)
- Dark mode support

### Design Tokens

```css
--primary: 243 75% 59%;      /* Deep indigo */
--secondary: 240 5% 96%;     /* Soft gray */
--accent: 35 92% 60%;        /* Warm amber */
```

### Rationale

1. **Consistency** - All components look cohesive
2. **Customizable** - CSS variables easy to change
3. **Familiar** - shadcn patterns widely adopted
4. **Complete** - Covers common UI patterns

### Philosophy

Design system is a **reference/guide**, not rigid constraint. Claude adapts patterns to specific needs while maintaining consistency.

---

## ADR-006: Multi-Source Design References

**Date:** 2024-12-12
**Status:** Accepted

### Context

Users may have existing design systems or want to reference specific sites.

### Decision

Support multiple reference sources (checked in order):
1. **Embedded skill** - Always available
2. **User URLs** - Fetched with WebFetch
3. **GitHub repos** - Clone or fetch raw files
4. **Local folder** - ~/design-systems/ if exists

### Rationale

1. **Flexibility** - Use any reference source
2. **Layered** - Embedded provides baseline
3. **Extensible** - Add more sources later
4. **Offline capable** - Embedded always works

---

## ADR-007: Why Not LangChain

**Date:** 2024-12-12
**Status:** Rejected (for this use case)

### Context

User asked why we didn't use LangChain/LangGraph for the Ollama pipeline.

### Analysis

LangChain provides:
- Prompt templates
- Chain composition
- Output parsers
- Memory/state management
- Tool calling abstractions

Our problems were:
- Models couldn't produce valid JSON
- Models copied examples verbatim
- Models ignored explicit instructions

### Decision

LangChain wouldn't have helped because:
- `JsonOutputParser` fails on the same malformed JSON
- Structured output features assume model CAN produce structured output
- It's an orchestration layer; our problem was model capability

### Where LangChain WOULD Help

- With better models (GPT-4, Claude) that follow instructions
- For complex multi-agent workflows with state machines
- For RAG pipelines with retrieval + generation
- For tool-calling agents that decide which tools to use

### Conclusion

A better conductor doesn't fix an orchestra that can't play their instruments.

For WebGen with Claude: Claude Code already IS an agent framework with tools, memory, and file operations. Adding LangChain would be redundant.

---

## ADR-008: Local Plugin Registration Requirements

**Date:** 2024-12-12
**Status:** Accepted

### Context

After creating the webgen plugin at `~/.claude/plugins/local-plugins/webgen/`, the `/webgen` command was not recognized. Investigation revealed that Claude Code doesn't auto-discover plugins from directories.

### Problem

Placing a plugin in `~/.claude/plugins/local-plugins/` is NOT sufficient. Plugins must be:
1. Part of a registered marketplace
2. Explicitly installed (registered in `installed_plugins_v2.json`)

### Discovery Process

1. Checked plugin structure - it was correct (`.claude-plugin/plugin.json`, `commands/`, `agents/`)
2. Compared with working plugins - structure matched
3. Noticed other local plugins (overnight-dev, system-toolkit) also had no commands - they were drafts too
4. Found no `marketplace.json` for local-plugins directory
5. Realized plugins need marketplace registration + installation entry

### Solution

Created the local plugin infrastructure:

1. **Marketplace manifest** at `~/.claude/plugins/local-plugins/.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "local-plugins",
     "version": "1.0.0",
     "description": "Locally developed Claude Code plugins",
     "plugins": ["webgen"]
   }
   ```

2. **Marketplace registration** in `~/.claude/plugins/known_marketplaces.json`:
   ```json
   "local-plugins": {
     "source": {
       "source": "local",
       "path": "/home/gs/.claude/plugins/local-plugins"
     },
     "installLocation": "/home/gs/.claude/plugins/local-plugins"
   }
   ```

3. **Plugin installation entry** in `~/.claude/plugins/installed_plugins_v2.json`:
   ```json
   "webgen@local-plugins": [{
     "scope": "user",
     "installPath": "/home/gs/.claude/plugins/local-plugins/webgen",
     "version": "1.0.0",
     "isLocal": true
   }]
   ```

### Key Files for Plugin Registration

| File | Purpose |
|------|---------|
| `~/.claude/plugins/known_marketplaces.json` | Lists all marketplace sources (git or local) |
| `~/.claude/plugins/installed_plugins_v2.json` | Tracks installed plugins with paths and versions |
| `{marketplace}/.claude-plugin/marketplace.json` | Lists plugins available in that marketplace |
| `{plugin}/.claude-plugin/plugin.json` | Plugin metadata (name, version, description) |

### Rationale

1. **No magic directories** - Explicit registration prevents accidental plugin loading
2. **Marketplace pattern** - Consistent with how remote plugins work
3. **Version tracking** - `installed_plugins_v2.json` tracks versions for updates
4. **Scope control** - Can install at user or project level

### Consequences

**For future local plugins:**
1. Create plugin in `~/.claude/plugins/local-plugins/{plugin-name}/`
2. Add plugin name to `marketplace.json` plugins array
3. Add installation entry to `installed_plugins_v2.json`
4. Restart Claude Code

### Cleanup

Removed stale incomplete `~/.claude/plugins/webgen/` directory (was at root level, created during earlier session before proper structure was established).
