# Contributing to GSC Plugins

This is a **publicly distributed Claude Code plugin marketplace**. All contributions must maintain platform agnosticism.

## The Golden Rule

**This package must work for ANY user on ANY system.**

Every path, hostname, domain, and identifier must be generic or configurable. No contributor's personal infrastructure should appear in the codebase.

## Agnosticism Checklist

Before submitting changes, verify:

### Paths
- [ ] No absolute paths with usernames (`/home/username/`, `/Users/username/`)
- [ ] Use `~` or `$HOME` for home directory references
- [ ] Use `~/projects/example` not `/home/gs/workspace/projects/example`

### Hostnames & Domains
- [ ] No internal domains (e.g., `*.internal.*`, `*.local`)
- [ ] Use `example.com` or environment variables for examples
- [ ] Replace `git.company.internal` with `${GITEA_URL}` or `gitea.example.com`

### Agent/System Names
- [ ] No hardcoded agent names tied to specific machines
- [ ] Use environment variables for multi-agent configurations
- [ ] Default to generic names like `claude` not `jarvis` or `alfred`

### Credentials & Secrets
- [ ] All secrets use environment variables
- [ ] No real emails, tokens, or API keys in examples
- [ ] Use placeholders: `your-token-here`, `user@example.com`

### Version Sync
- [ ] `plugins/{name}/.claude-plugin/plugin.json` version is updated
- [ ] `.claude-plugin/marketplace.json` version matches
- [ ] `README.md` plugin table shows correct version

## Common Violations

| Bad | Good |
|-----|------|
| `/home/gs/workspace/` | `~/projects/` |
| `git.internal.muhaha.dev` | `${GITEA_URL}` or `gitea.example.com` |
| `ssh ubuntu-mini` | Use environment-based detection |
| `return "jarvis"` | `return os.environ.get("AGENT_NAME", "claude")` |
| `email: "gs@ubuntu-mini"` | `name: "gaurangrshah"` (email optional) |

## Environment Variable Pattern

When features need user-specific configuration:

```python
# Good: Configurable with sensible default
agent_name = os.environ.get("WORKLOG_AGENT_NAME", "claude")

# Good: Configurable mapping for advanced users
hostname_map = os.environ.get("WORKLOG_HOSTNAME_MAP", "")
```

```markdown
<!-- Good: Documentation shows env var pattern -->
| Variable | Default | Description |
|----------|---------|-------------|
| `GITEA_URL` | - | Your Gitea instance URL |
| `AGENT_NAME` | `claude` | Agent identifier for multi-agent setups |
```

## AI Agent Instructions

If you're an AI agent working on this codebase:

1. **This is NOT an internal tool** - It's a public package indexed on claude-plugins.dev
2. **Never reference the author's infrastructure** - No internal domains, hostnames, or paths
3. **Test with fresh perspective** - Would this work for someone who just discovered this package?
4. **Environment variables > hardcoding** - If something varies by user, make it configurable
5. **Check before committing** - Run `grep -rE "/home/\w+|\.internal\.|ubuntu-mini|atlas" plugins/` to catch violations

## Pre-Commit Check

Run this before any commit:

```bash
# Should return no matches
grep -rE "/home/\w+|\.internal\.|ubuntu-mini|\.local\." plugins/

# Verify marketplace.json versions match plugin.json
for plugin in plugins/*/; do
  name=$(basename "$plugin")
  actual=$(jq -r '.version' "$plugin/.claude-plugin/plugin.json" 2>/dev/null)
  listed=$(jq -r ".plugins[] | select(.name==\"$name\") | .version" .claude-plugin/marketplace.json 2>/dev/null)
  if [ "$actual" != "$listed" ]; then
    echo "VERSION MISMATCH: $name - plugin.json=$actual marketplace.json=$listed"
  fi
done
```

## Why This Matters

- **Trust**: Users expect a marketplace package to be production-ready
- **Portability**: Works on macOS, Linux, Windows WSL without modification
- **Professionalism**: No "works on my machine" issues
- **Maintainability**: Clear separation between development and distribution

## Questions?

If you're unsure whether something is agnostic enough, ask:

> "Would this work if someone in Tokyo installed this plugin tomorrow with no knowledge of my setup?"

If no, make it configurable.
