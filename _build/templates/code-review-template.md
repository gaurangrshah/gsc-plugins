# Code Review Template

Standard output format for code reviewer agents. Ensures consistent, actionable reviews.

## Review Categories

### 1. Critical Issues (Must Fix)
Issues that block merge or deployment.

```markdown
#### CRITICAL: [Issue Title]
**Location:** `path/to/file.ts:42`
**Issue:** [Clear description of the problem]
**Impact:** [Security vulnerability | Data loss | System crash | etc.]
**Fix:** [Specific remediation steps]
```

### 2. Important Issues (Should Fix)
Issues that affect quality but don't block.

```markdown
#### IMPORTANT: [Issue Title]
**Location:** `path/to/file.ts:42`
**Issue:** [Clear description]
**Impact:** [Performance | Maintainability | etc.]
**Suggestion:** [Recommended fix]
```

### 3. Minor Issues (Nice to Fix)
Style, conventions, minor improvements.

```markdown
#### MINOR: [Issue Title]
**Location:** `path/to/file.ts:42`
**Suggestion:** [Brief recommendation]
```

### 4. Positive Observations
Good patterns worth noting.

```markdown
#### GOOD: [Pattern Name]
**Location:** `path/to/file.ts`
**Note:** [What was done well and why]
```

## Review Checklist

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection where applicable
- [ ] Authentication/authorization checks
- [ ] Secure password handling

### Performance
- [ ] No N+1 queries
- [ ] Appropriate indexing for queries
- [ ] No blocking operations in async code
- [ ] Reasonable memory usage
- [ ] Caching where appropriate

### Code Quality
- [ ] Clear, descriptive naming
- [ ] Functions under 50 lines
- [ ] Single responsibility principle
- [ ] DRY - no excessive duplication
- [ ] Proper error handling
- [ ] Type safety (if TypeScript)

### Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for APIs
- [ ] Edge cases covered
- [ ] Error scenarios tested

### Documentation
- [ ] Complex logic has comments
- [ ] Public APIs documented
- [ ] README updated if needed

## Summary Format

```markdown
## Review Summary

**Files Reviewed:** X
**Critical Issues:** X
**Important Issues:** X
**Minor Issues:** X

### Verdict: [APPROVE | REQUEST_CHANGES | COMMENT]

[Brief overall assessment and key points]
```

## Confidence Scoring

Rate confidence in the review:
- **HIGH:** Familiar codebase, clear patterns
- **MEDIUM:** Some unfamiliar areas, reasonable assumptions
- **LOW:** Limited context, recommend additional review

---

**Template Version:** 1.0
**Used By:** appgen-code-reviewer, webgen-code-reviewer
**Lines:** ~100
