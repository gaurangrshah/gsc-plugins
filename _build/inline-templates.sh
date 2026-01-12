#!/usr/bin/env bash
#
# inline-templates.sh - Copy templates into agent instructions during build
#
# This script inlines shared templates and frameworks into plugin agents,
# reducing duplication while keeping agents self-contained for distribution.
#
# Usage:
#   ./inline-templates.sh [--dry-run] [--verbose] [plugin-name]
#
# Examples:
#   ./inline-templates.sh                    # Build all plugins
#   ./inline-templates.sh appgen             # Build appgen only
#   ./inline-templates.sh --dry-run          # Show what would be done
#   ./inline-templates.sh --verbose appgen   # Verbose output for appgen

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR"
PLUGINS_DIR="$(dirname "$SCRIPT_DIR")/plugins"
TEMPLATES_DIR="$BUILD_DIR/templates"
FRAMEWORKS_DIR="$BUILD_DIR/frameworks"

# Options
DRY_RUN=false
VERBOSE=false
TARGET_PLUGIN=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
log_verbose() { [[ "$VERBOSE" == "true" ]] && echo -e "${BLUE}[VERBOSE]${NC} $1" || true; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [--verbose] [plugin-name]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be done without making changes"
            echo "  --verbose    Show detailed output"
            echo "  --help       Show this help message"
            echo ""
            echo "Arguments:"
            echo "  plugin-name  Optional: Build specific plugin only (appgen, webgen, etc.)"
            exit 0
            ;;
        *)
            TARGET_PLUGIN="$1"
            shift
            ;;
    esac
done

# Verify directories exist
verify_setup() {
    log_info "Verifying build setup..."

    if [[ ! -d "$TEMPLATES_DIR" ]]; then
        log_error "Templates directory not found: $TEMPLATES_DIR"
        exit 1
    fi

    if [[ ! -d "$FRAMEWORKS_DIR" ]]; then
        log_error "Frameworks directory not found: $FRAMEWORKS_DIR"
        exit 1
    fi

    if [[ ! -d "$PLUGINS_DIR" ]]; then
        log_error "Plugins directory not found: $PLUGINS_DIR"
        exit 1
    fi

    log_verbose "Templates: $TEMPLATES_DIR"
    log_verbose "Frameworks: $FRAMEWORKS_DIR"
    log_verbose "Plugins: $PLUGINS_DIR"
}

# Get template content between markers, or full file if no markers
get_template_content() {
    local template_file="$1"
    local start_marker="${2:-}"
    local end_marker="${3:-}"

    if [[ -z "$start_marker" ]]; then
        # Return full file content (skip first line if it's a # header)
        tail -n +2 "$template_file"
    else
        # Extract between markers
        sed -n "/$start_marker/,/$end_marker/p" "$template_file" | tail -n +2 | head -n -1
    fi
}

# Inline a template into an agent file
inline_template() {
    local agent_file="$1"
    local template_name="$2"
    local placeholder="$3"

    local template_file="$TEMPLATES_DIR/$template_name"

    if [[ ! -f "$template_file" ]]; then
        log_warn "Template not found: $template_name"
        return 1
    fi

    if ! grep -q "$placeholder" "$agent_file" 2>/dev/null; then
        log_verbose "Placeholder not found in $agent_file: $placeholder"
        return 0
    fi

    log_verbose "Inlining $template_name into $agent_file"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would inline $template_name -> $agent_file"
        return 0
    fi

    # Create temp file with inlined content
    local temp_file=$(mktemp)
    local template_content=$(cat "$template_file")

    # Use awk to replace placeholder with template content
    awk -v placeholder="$placeholder" -v content="$template_content" '
        $0 ~ placeholder { print content; next }
        { print }
    ' "$agent_file" > "$temp_file"

    mv "$temp_file" "$agent_file"
    log_success "Inlined $template_name"
}

# Inline a framework into an agent file
inline_framework() {
    local agent_file="$1"
    local framework_name="$2"
    local placeholder="$3"

    local framework_file="$FRAMEWORKS_DIR/$framework_name"

    if [[ ! -f "$framework_file" ]]; then
        log_warn "Framework not found: $framework_name"
        return 1
    fi

    if ! grep -q "$placeholder" "$agent_file" 2>/dev/null; then
        log_verbose "Placeholder not found in $agent_file: $placeholder"
        return 0
    fi

    log_verbose "Inlining framework $framework_name into $agent_file"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would inline framework $framework_name -> $agent_file"
        return 0
    fi

    # Create temp file with inlined content
    local temp_file=$(mktemp)
    local framework_content=$(cat "$framework_file")

    awk -v placeholder="$placeholder" -v content="$framework_content" '
        $0 ~ placeholder { print content; next }
        { print }
    ' "$agent_file" > "$temp_file"

    mv "$temp_file" "$agent_file"
    log_success "Inlined framework $framework_name"
}

# Process a single plugin
process_plugin() {
    local plugin_name="$1"
    local plugin_dir="$PLUGINS_DIR/$plugin_name"

    if [[ ! -d "$plugin_dir" ]]; then
        log_warn "Plugin directory not found: $plugin_dir"
        return 1
    fi

    log_info "Processing plugin: $plugin_name"

    # Find all agent files
    local agents_dir="$plugin_dir/agents"
    if [[ ! -d "$agents_dir" ]]; then
        log_verbose "No agents directory for $plugin_name"
        return 0
    fi

    # Process each agent file
    for agent_file in "$agents_dir"/*.md; do
        [[ -f "$agent_file" ]] || continue

        local agent_name=$(basename "$agent_file" .md)
        log_verbose "Checking agent: $agent_name"

        # Check for template placeholders and inline them
        # Format: <!-- INLINE:template-name.md -->
        while IFS= read -r line; do
            if [[ "$line" =~ \<!--\ INLINE:([a-z-]+\.md)\ --\> ]]; then
                local template="${BASH_REMATCH[1]}"
                inline_template "$agent_file" "$template" "$line"
            fi
            if [[ "$line" =~ \<!--\ FRAMEWORK:([a-z-]+\.md)\ --\> ]]; then
                local framework="${BASH_REMATCH[1]}"
                inline_framework "$agent_file" "$framework" "$line"
            fi
        done < "$agent_file"
    done

    log_success "Completed: $plugin_name"
}

# Main build process
main() {
    log_info "GSC Plugins Build System"
    log_info "========================"

    [[ "$DRY_RUN" == "true" ]] && log_warn "DRY RUN MODE - No changes will be made"

    verify_setup

    # List available templates
    log_info "Available templates:"
    for t in "$TEMPLATES_DIR"/*.md; do
        [[ -f "$t" ]] && log_verbose "  - $(basename "$t")"
    done

    log_info "Available frameworks:"
    for f in "$FRAMEWORKS_DIR"/*.md; do
        [[ -f "$f" ]] && log_verbose "  - $(basename "$f")"
    done

    # Process plugins
    if [[ -n "$TARGET_PLUGIN" ]]; then
        process_plugin "$TARGET_PLUGIN"
    else
        log_info "Processing all plugins..."
        for plugin_dir in "$PLUGINS_DIR"/*/; do
            [[ -d "$plugin_dir" ]] || continue
            local plugin_name=$(basename "$plugin_dir")
            process_plugin "$plugin_name"
        done
    fi

    log_success "Build complete!"

    # Show summary
    echo ""
    log_info "Summary:"
    log_info "  Templates: $(ls -1 "$TEMPLATES_DIR"/*.md 2>/dev/null | wc -l)"
    log_info "  Frameworks: $(ls -1 "$FRAMEWORKS_DIR"/*.md 2>/dev/null | wc -l)"
    log_info "  Plugins processed: $(ls -1d "$PLUGINS_DIR"/*/ 2>/dev/null | wc -l)"
}

# Run main
main
