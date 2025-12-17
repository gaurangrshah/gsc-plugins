---
name: worktree-workflow
description: Git worktree setup, management, and cleanup for isolated parallel development
---

# Worktree Workflow Skill

Enables isolated development using git worktrees. Each project runs in its own directory with full git history but no interference with other work.

---

## When to Recommend Worktrees

**Offer worktrees when:**
- User has multiple projects/tasks in progress
- Working in a shared/team repository
- Project generation might conflict with ongoing work
- User wants to preserve current branch state
- Long-running generation that shouldn't block other work

**Skip worktrees when:**
- Fresh/empty output directory with no existing work
- User explicitly wants to work in main directory
- Simple single-file or component generation
- User declines worktree option

---

## Worktree Setup Protocol

### 1. Pre-Flight Check

Before creating worktree, verify:

```bash
# Check if we're in a git repo
git rev-parse --git-dir 2>/dev/null || echo "NOT_GIT_REPO"

# Check current branch
git branch --show-current

# Check for uncommitted changes
git status --porcelain
```

**If not a git repo:** Initialize one or use standard workflow (no worktree needed for new projects).

**If uncommitted changes:** Warn user - worktrees work best with clean state.

### 2. Create Worktree

```bash
# Standard pattern: worktrees live in sibling directory
PROJECT_DIR="${OUTPUT_DIR}/${slug} - ${generator}"
WORKTREE_DIR="${OUTPUT_DIR}/worktrees/${slug}"
BRANCH_NAME="feat/${slug}"

# Ensure worktrees directory exists
mkdir -p "${OUTPUT_DIR}/worktrees"

# Create worktree with new branch
git worktree add -b "${BRANCH_NAME}" "${WORKTREE_DIR}" main

# Navigate to worktree
cd "${WORKTREE_DIR}"
```

### 3. Verify Worktree Creation

```bash
# List all worktrees (should show new one)
git worktree list

# Verify we're on the correct branch
git branch --show-current  # Should be: feat/${slug}

# Verify isolation
pwd  # Should be in worktrees directory
```

---

## Working in Worktree

### Directory Structure

```
${OUTPUT_DIR}/
├── worktrees/
│   └── ${slug}/          # Isolated worktree
│       ├── .git          # Worktree git link (NOT full .git)
│       └── [project files]
├── main-project/         # Main checkout (if exists)
└── .git/                 # Shared git directory
```

### Committing in Worktree

Same as normal git workflow - worktrees share history:

```bash
cd "${WORKTREE_DIR}"
git add .
git commit -m "feat(${slug}): description"
git push -u origin "feat/${slug}"
```

---

## Worktree Cleanup Protocol (MANDATORY)

**CRITICAL:** Agents MUST clean up worktrees and merged branches. Orphaned worktrees waste disk space and create confusion.

### After Successful Completion

```bash
# 1. Ensure all changes committed and pushed
git status --porcelain  # Must be empty

# 2. Switch to main in the MAIN worktree (not this worktree)
cd "${OUTPUT_DIR}"  # Back to main project area
git checkout main
git pull origin main

# 3. Merge the feature branch
git merge "feat/${slug}" --no-ff -m "Merge feat/${slug}: ${description}"

# 4. Push merged main
git push origin main

# 5. Delete the remote branch
git push origin --delete "feat/${slug}"

# 6. Remove the worktree
git worktree remove "${WORKTREE_DIR}"

# 7. Delete the local branch
git branch -d "feat/${slug}"

# 8. Prune stale worktree references
git worktree prune
```

### Cleanup Verification

```bash
# Verify worktree removed
git worktree list  # Should NOT include the removed worktree

# Verify branch deleted
git branch -a | grep "feat/${slug}"  # Should return nothing

# Verify merge happened
git log --oneline -3  # Should show merge commit
```

### Failed/Abandoned Worktree Cleanup

If user abandons or generation fails:

```bash
# Force remove worktree (if changes not worth keeping)
git worktree remove --force "${WORKTREE_DIR}"

# Delete the branch
git branch -D "feat/${slug}"  # -D for force delete

# Prune references
git worktree prune
```

---

## Orchestrator Integration

### Checkpoint 1: Requirements (Add to existing)

After requirements confirmed, add this prompt:

```markdown
**Worktree Option:**

I can generate this project in an isolated git worktree, which:
- Keeps your current work untouched
- Creates a separate directory for this project
- Allows parallel development
- Merges back to main when complete

Would you like to use a git worktree? (Recommended if you have work in progress)
- **Yes** - Create isolated worktree
- **No** - Use standard feature branch in output directory
```

### Store Worktree Context

If user chooses worktree, store in session:

```json
{
  "use_worktree": true,
  "worktree_path": "${OUTPUT_DIR}/worktrees/${slug}",
  "branch_name": "feat/${slug}",
  "main_path": "${OUTPUT_DIR}"
}
```

### Final Phase: Add Cleanup Step

Before marking project complete:

```markdown
## WORKTREE CLEANUP

**Worktree:** ${worktree_path}
**Branch:** ${branch_name}

Cleanup steps:
1. Verify all changes committed
2. Merge to main
3. Push main
4. Delete remote branch
5. Remove worktree
6. Delete local branch
7. Prune references

Executing cleanup...
```

---

## Error Handling

### Worktree Already Exists

```bash
# Check if worktree exists
git worktree list | grep "${slug}" && echo "EXISTS"

# If exists, offer options:
# 1. Use existing worktree (continue previous work)
# 2. Remove and recreate (fresh start)
# 3. Use different name
```

### Branch Already Exists

```bash
# Check if branch exists
git branch -a | grep "feat/${slug}" && echo "BRANCH_EXISTS"

# If exists locally only: can checkout
# If exists on remote: need to fetch and merge or use different name
```

### Merge Conflicts

```markdown
## MERGE CONFLICT DETECTED

The worktree branch has conflicts with main.

**Conflicting files:**
- [list files]

**Options:**
1. Resolve conflicts (I'll help)
2. Force merge (may lose main changes)
3. Keep worktree, skip merge (manual resolution later)
4. Abandon worktree changes

Your choice?
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| List worktrees | `git worktree list` |
| Create worktree | `git worktree add -b BRANCH PATH BASE` |
| Remove worktree | `git worktree remove PATH` |
| Force remove | `git worktree remove --force PATH` |
| Prune stale | `git worktree prune` |
| Check branch | `git branch --show-current` |

---

## Hygiene Checklist (For Agents)

Before ending ANY session with worktrees:

- [ ] All worktree changes committed?
- [ ] Worktree branch pushed to remote?
- [ ] If complete: Merged to main?
- [ ] If complete: Remote branch deleted?
- [ ] If complete: Worktree removed?
- [ ] If complete: Local branch deleted?
- [ ] `git worktree prune` run?
- [ ] `git worktree list` shows expected state?

**Rule:** Never leave orphaned worktrees. Either merge+cleanup OR explicitly document for user to handle later.
