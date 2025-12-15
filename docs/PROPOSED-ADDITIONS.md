# Proposed Additions to GSC Plugins Ecosystem

Based on analysis of the internal `~/.claude` agentic system, here are components worth packaging for the gsc-plugins ecosystem.

## Executive Summary

The internal system has several battle-tested components that would provide value to the broader Claude Code community. The most valuable are:

1. **Orchestrator Agent** - Creator ↔ Reviewer coordination with 2-iteration max
2. **Deployment Verification Protocol** - 5-layer verification for deployments
3. **Scope Guardrails Protocol** - RED/YELLOW/GREEN zone system
4. **Documentation Hygiene Skill** - README-driven navigation system

## Recommended Additions

### 1. ~~orchestrator-plugin~~ (NOT Recommended)

**Status:** After analysis, this is NOT recommended for packaging.

**Reason:** WebGen and AppGen already have domain-specific orchestrators (`webgen-orchestrator.md`, `appgen-orchestrator.md`) that implement the same core pattern (2-iteration max + human arbitration) but with valuable domain-specific adaptations:

| Orchestrator | Checkpoints | Domain Features |
|--------------|-------------|-----------------|
| Generic | 3 (Specs, Implementation, Final) | Multi-domain references |
| WebGen | 5 | Asset extraction, competitive research, legal pages |
| AppGen | 8 | Database design, API design, auth strategies, testing, deployment |

**Alternative:** Document the orchestrator pattern in the main gsc-plugins README as an architectural pattern that existing plugins follow. New plugin authors can reference `AGENT_ORCHESTRATION_FRAMEWORK.md` when building their own domain-specific orchestrators.

---

### 2. deployment-toolkit (High Priority)

**Source:** `~/.claude/protocols/DEPLOYMENT-VERIFICATION-PROTOCOL.md`

**What it does:**
- 5-layer verification framework for deployments
- Layer 1: Infrastructure Health
- Layer 2: Network Accessibility
- Layer 3: Application Bootstrap
- Layer 4: Browser/Client Testing
- Layer 5: End-to-End Workflow

**Why valuable:**
- Prevents "containers running but app broken" situations
- Universal for Docker, Kubernetes, serverless
- Includes common failure patterns and solutions
- Research-first approach guidance

**Components:**
- Protocol: `DEPLOYMENT-VERIFICATION-PROTOCOL.md`
- Skill: deployment-verifier (to be created)
- Command: `/verify-deployment`

---

### 3. scope-guardrails (Medium Priority)

**Source:** `~/.claude/protocols/SCOPE-GUARDRAILS.md`

**What it does:**
- Traffic light system for operation classification
- 🟢 GREEN: Auto-approved (safe, additive, reversible)
- 🟡 YELLOW: Ask first (breaking changes, wide impact)
- 🔴 RED: Hard stop (destructive, irreversible)

**Why valuable:**
- Prevents scope creep and inadvertent changes
- Clear decision framework for agents
- Reduces "while I'm here..." syndrome
- Customizable per project

**Components:**
- Protocol: `SCOPE-GUARDRAILS.md`
- Hook: scope-check (verify operations against guardrails)

---

### 4. docs-hygiene (Medium Priority)

**Source:** `~/.claude/plugins/local-plugins/*/skills/docs-manager/SKILL.md`

**What it does:**
- README-driven navigation system
- Every directory has README with paths, descriptions, usage
- Traversable documentation structure
- Validation scripts for README hygiene

**Why valuable:**
- Living documentation of current system state
- Easy onboarding for new projects
- Prevents documentation drift
- Integrates with existing docs-manager

**Components:**
- Skill: docs-hygiene
- Command: `/docs-validate`
- Hook: pre-commit docs check

---

## Lower Priority / Future Consideration

### verify-first-protocol

**Source:** `~/.claude/protocols/VERIFY-FIRST-PROTOCOL.md`

Simple but valuable principle: verify current state before making changes.
Could be bundled with scope-guardrails.

### system-analyzer

**Source:** `~/.claude/skills/system-analyzer/`

Captures system baselines and detects changes.
Very environment-specific (ubuntu-focused), may need generalization.

### agent-comms

**Source:** `~/.claude/skills/agent-comms/`

Cross-system agent coordination.
Complex, requires shared infrastructure.

---

## Integration Patterns

### With Existing GSC Plugins

| New Component | Integrates With | How |
|---------------|-----------------|-----|
| orchestrator | webgen, appgen | Quality gates during generation |
| deployment-toolkit | appgen | Post-deployment verification |
| scope-guardrails | all | Operation classification |
| docs-hygiene | worklog | Cross-reference with knowledge base |

### With TaskFlow

```
/task-parse PRD
    ↓
orchestrator coordinates implementation
    ↓
deployment-toolkit verifies
    ↓
/task-status done
```

---

## Implementation Recommendations

### Phase 1 (Immediate)

1. **orchestrator-plugin**
   - Package orchestrator agent + framework
   - Add as standalone plugin
   - Document integration with webgen/appgen

2. **deployment-toolkit**
   - Package protocol as skill
   - Create /verify-deployment command
   - Document common scenarios

### Phase 2 (Short-term)

3. **scope-guardrails**
   - Package as protocol + hook
   - Make customizable per project
   - Document RED/YELLOW/GREEN examples

4. **docs-hygiene**
   - Extract from internal toolkit
   - Generalize for any project
   - Create validation tooling

### Phase 3 (Medium-term)

5. Evaluate remaining components
6. Consider cross-plugin hooks
7. Build integration test suite

---

## Non-Recommendations

The following components are NOT recommended for packaging:

| Component | Reason |
|-----------|--------|
| jarvis agent | Too environment-specific (Coolify, homelab) |
| desktop-manager | Omakub-specific |
| system-analyzer | Ubuntu-specific baselines |
| dotfiles-manager | Personal workflow, not universal |
| gemini-cli | External API integration, niche use case |
| youtube-transcript | Niche use case |
| image-generation | External API integration |

---

## Next Steps

1. [ ] Validate proposed additions with user
2. [ ] Prioritize Phase 1 components
3. [ ] Create plugin scaffolds for approved additions
4. [ ] Document integration patterns
5. [ ] Test with existing GSC plugins
6. [ ] Publish to gsc-plugins marketplace

---

**Created:** 2025-12-14
**Author:** Claude Code agent
**Status:** Draft proposal
