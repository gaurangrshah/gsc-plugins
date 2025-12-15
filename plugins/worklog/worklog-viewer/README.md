# Worklog Database Viewer

Browser-based SQLite viewer for the worklog knowledge persistence system with optional GitHub document integration.

## Features

### Database Viewer
- **Natural Language Search** - Type multiple terms to filter (e.g., "debugging react") - all terms must match
- **Tag Filtering** - Click tags to filter by system/agent identifiers
- **Markdown Rendering** - Content fields render as formatted markdown with syntax highlighting
- **View Toggle** - Switch between rendered and raw views for markdown content
- **Dark/Light Theme** - Toggle with persistence
- **Database Caching** - Loaded database persists in IndexedDB across page refreshes
- **Custom SQL Queries** - Run arbitrary SQL with Ctrl+Enter
- **CSV Export** - Export filtered results
- **Auto Table Discovery** - Works with any SQLite database structure

### GitHub Document Browser (Optional)
- **Multi-System Support** - Browse docs from different system branches
- **Private Repo Access** - Use Personal Access Token for private repos
- **Markdown Rendering** - View rendered documentation with syntax highlighting
- **File Browser** - Navigate directory structure from GitHub

## Usage

### Basic (Local Database)
1. Open `index.html` in a browser
2. Click "Load Database" and select your `worklog.db` file
3. Use search, tag filters, and sort controls to explore data
4. Double-click any row to view full details

### GitHub Document Browser
1. Click "Set Token" to add your GitHub PAT (with `repo` scope for private repos)
2. Select a branch/system from the dropdown
3. Browse and view markdown documentation

## Database Location

| Setup | Default Path |
|-------|--------------|
| Local (default) | `~/.claude/worklog/worklog.db` |
| Shared (network) | Your configured shared path |

## Configuration

The viewer can be configured via environment variables set during plugin install:

| Variable | Default | Description |
|----------|---------|-------------|
| `WORKLOG_MODE` | `local` | `local` or `shared` - controls multi-system features |
| `GITHUB_REPO` | (none) | GitHub repo for document browser (e.g., `user/repo`) |
| `GITHUB_BRANCHES` | `main` | Comma-separated list of branches to show |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Enter` | Run SQL query |
| `Escape` | Close modal |

## Technical Details

- **SQL.js** - SQLite compiled to WebAssembly for browser execution
- **Marked.js** - Markdown parser for rendering content fields
- **Highlight.js** - Syntax highlighting for code blocks
- **DOMPurify** - HTML sanitization for XSS protection
- **IndexedDB** - Caches loaded database for persistence
- **localStorage** - Stores theme preference, last selected table, and GitHub token
- **Single HTML file** - All libraries loaded from CDN

## Building

The source viewer is in the NAS logs directory. To build and copy to plugins:

```bash
./build.sh
```

This minifies the HTML and copies to:
- `/home/gs/projects/gsc-plugins/plugins/worklog/worklog-viewer/`
- `~/.claude/plugins/local-plugins/worklog/worklog-viewer/` (if exists)

## Related

- [Worklog Plugin Documentation](../README.md)
- [Schema Reference](../schema/)
