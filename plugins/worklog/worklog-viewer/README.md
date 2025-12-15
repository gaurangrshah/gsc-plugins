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
1. Click the **Settings** (gear icon) to configure:
   - **GitHub Repository** - Format: `owner/repo` (e.g., `username/my-docs`)
   - **Branches** - Comma-separated list of branches to show in dropdown
2. Click **Token** to add your GitHub PAT (with `repo` scope for private repos)
3. Select a branch from the dropdown
4. Enter a document path or click **Browse** to navigate the repository

## Database Location

| Setup | Default Path |
|-------|--------------|
| Local (default) | `~/.claude/worklog/worklog.db` |
| Shared (network) | Your configured shared path |

## Configuration

All settings are configured via the **Settings** modal (gear icon) and stored in browser localStorage:

| Setting | Storage Key | Description |
|---------|-------------|-------------|
| GitHub Repository | `worklog-github-repo` | Repository in `owner/repo` format |
| Branches | `worklog-branches` | JSON array of branch names |
| GitHub Token | `github-token` | Personal Access Token for private repos |
| Theme | `worklog-theme` | `dark` or `light` |
| Last Table | `worklog-last-table` | Last viewed database table |

### First-Time Setup

1. Open the viewer in your browser
2. Click the **Settings** gear icon
3. Enter your GitHub repository (e.g., `username/my-docs`)
4. Add branches you want to access (comma-separated)
5. Click **Save Settings**
6. (Optional) Click **Token** to add a PAT for private repository access

Settings persist across browser sessions.

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
