# Worklog Database Viewer

Browser-based SQLite viewer for the worklog knowledge persistence system.

## Features

- **Natural Language Search** - Type multiple terms to filter (e.g., "debugging react") - all terms must match
- **Tag Filtering** - Click tags to filter by system/agent identifiers
- **Dark/Light Theme** - Toggle with persistence
- **Database Caching** - Loaded database persists in IndexedDB across page refreshes
- **Custom SQL Queries** - Run arbitrary SQL with Ctrl+Enter
- **CSV Export** - Export filtered results
- **Auto Table Discovery** - Works with any SQLite database structure

## Usage

1. Open `index.html` in a browser
2. Click "Load Database" and select your `worklog.db` file
3. Use search, tag filters, and sort controls to explore data
4. Double-click any row to view full details

## Database Location

The default worklog database location depends on your setup:

| Setup | Default Path |
|-------|--------------|
| Local (default) | `~/.claude/worklog/worklog.db` |
| Shared (network) | Your configured shared path |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Enter` | Run SQL query |
| `Escape` | Close modal |

## Technical Details

- **SQL.js** - SQLite compiled to WebAssembly for browser execution
- **IndexedDB** - Caches loaded database for persistence
- **localStorage** - Stores theme preference and last selected table
- **No dependencies** - Single HTML file, loads SQL.js from CDN

## Related

- [Worklog Plugin Documentation](../README.md)
- [Schema Reference](../schema/)
