# Orchestration Protocol

Standard protocol for multi-phase project orchestration. This template is inlined into orchestrator agents during build.

## Checkpoint System

All orchestrated projects follow these checkpoints:

### CHECKPOINT 1: Project Initialization
- [ ] Validate requirements and scope
- [ ] Check for existing configuration (`.local.md`)
- [ ] Query knowledge base for relevant context
- [ ] Set up project structure
- [ ] Initialize tracking (TaskFlow if available)

### CHECKPOINT 2: Research & Planning
- [ ] Analyze requirements thoroughly
- [ ] Query KB for similar past projects
- [ ] Identify architectural decisions needed
- [ ] Document technology choices with rationale
- [ ] Create implementation plan

### CHECKPOINT 3: Implementation
- [ ] Execute plan phase by phase
- [ ] Validate each phase before proceeding
- [ ] Document decisions as they're made
- [ ] Store learnings to knowledge base
- [ ] Update progress tracking

### CHECKPOINT 4: Review & Validation
- [ ] Run code review (invoke reviewer agent)
- [ ] Execute test suite
- [ ] Validate against original requirements
- [ ] Check for security issues
- [ ] Verify documentation completeness

### CHECKPOINT 5: Completion
- [ ] Generate final documentation
- [ ] Store project learnings to KB
- [ ] Clean up temporary artifacts
- [ ] Provide user summary
- [ ] Archive or hand off

## State Management

```
PROJECT_STATE = {
  checkpoint: 1-5,
  phase: current implementation phase,
  blockers: [],
  decisions: [],
  artifacts: []
}
```

## Error Recovery

When errors occur:
1. Log error with full context
2. Determine if recoverable
3. If recoverable: attempt fix, retry
4. If not: pause, notify user, await guidance

## Communication Protocol

### To User
- Brief status at each checkpoint
- Detailed output only when requested
- Clear indication of blockers
- Actionable next steps

### To Sub-Agents
- Full context in prompts
- Clear success criteria
- Expected output format
- Error handling instructions

## Knowledge Base Integration

```markdown
At each checkpoint:
1. Query: mcp__worklog__recall_context(topic="project-type")
2. Apply: Use relevant patterns from past projects
3. Store: mcp__worklog__store_knowledge() for new learnings
```

## Progress Tracking

If TaskFlow available:
```bash
/task-status {task-id} in_progress  # At checkpoint start
/task-status {task-id} done         # At checkpoint complete
```

If TodoWrite only:
- Update todo items as checkpoints complete
- Maintain single in_progress item

---

**Template Version:** 1.0
**Used By:** appgen-orchestrator, webgen-orchestrator
**Lines:** ~90
