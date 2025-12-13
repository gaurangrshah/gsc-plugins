---
description: Change worklog profile or settings after initial setup
arguments:
  - name: setting
    description: "Setting to change: profile, path, or show"
    required: false
---

# Worklog Configure

Modify worklog settings after initial setup. Use to upgrade/downgrade profile or change database path.

## Usage

```
/worklog-configure              # Interactive menu
/worklog-configure profile      # Change profile only
/worklog-configure show         # Show current settings
```

## Workflow

### Step 1: Read Current Configuration

Load settings from `.claude/worklog.local.md`:

```bash
# Extract YAML frontmatter
head -20 ~/.claude/worklog.local.md
```

Parse:
- `profile`: current profile (minimal/standard/full)
- `db_path`: database location
- `mode`: local or shared

### Step 2: Show Current Settings (if `show` or no arg)

```
Current Worklog Configuration:

Profile:  {profile}
Database: {db_path}
Mode:     {mode}
System:   {system_name}

Tables available: {count}
Entries logged:   {count}
Knowledge items:  {count}

What would you like to change?
[1] Profile (minimal/standard/full)
[2] Database path
[3] Exit
```

### Step 3: Handle Profile Change

If changing profile:

**Upgrading (minimal → standard, or standard → full):**
- If upgrading to FULL and extended tables don't exist:
  ```bash
  sqlite3 {db_path} < {plugin_root}/schema/extended.sql
  ```
- Replace CLAUDE.md section with new profile template

**Downgrading (full → standard, or standard → minimal):**
- Tables remain (no data loss)
- Only CLAUDE.md section changes
- Warn user: "Boot queries and auto-store will be reduced"

### Step 4: Handle Path Change

If changing database path:

```
WARNING: Changing database path means:
- You'll lose connection to current database
- History will not be migrated automatically

Continue? (y/n)
```

If yes:
1. Verify new path exists and is accessible
2. Update `.claude/worklog.local.md`
3. Update CLAUDE.md with new path
4. Test connectivity

### Step 5: Update Configuration File

Rewrite `.claude/worklog.local.md` with new settings:

```markdown
---
profile: {new_profile}
db_path: {new_path}
mode: {mode}
system_name: {system_name}
initialized: {original_timestamp}
last_modified: {now}
---

# Worklog Configuration

## Current Settings
- **Profile:** {profile}
- **Database:** {db_path}
- **Mode:** {mode}

## Change History
- {timestamp}: Profile changed from {old} to {new}
```

### Step 6: Update CLAUDE.md

Remove existing worklog section (between markers):
```
<!-- WORKLOG_START -->
...
<!-- WORKLOG_END -->
```

Insert new profile template.

### Step 7: Confirm Changes

```
Configuration updated!

Changed:
- Profile: {old} → {new}

Run `/worklog-status` to verify.
```

$ARGUMENTS
