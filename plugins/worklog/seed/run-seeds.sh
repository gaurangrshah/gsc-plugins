#!/bin/bash
# Worklog Seed Data Loader
# Usage: ./run-seeds.sh [sqlite|postgresql] [db_path_or_url]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="${1:-sqlite}"
DB_PATH="${2:-$HOME/.claude/worklog/worklog.db}"

echo "Loading worklog seed data..."
echo "Backend: $BACKEND"

if [ "$BACKEND" = "sqlite" ]; then
    if [ ! -f "$DB_PATH" ]; then
        echo "Error: Database not found at $DB_PATH"
        echo "Run schema creation first."
        exit 1
    fi

    echo "Loading tag_taxonomy..."
    sqlite3 "$DB_PATH" < "$SCRIPT_DIR/tag_taxonomy.sql"

    echo "Loading topics..."
    sqlite3 "$DB_PATH" < "$SCRIPT_DIR/topics.sql"

    echo "Loading knowledge..."
    sqlite3 "$DB_PATH" < "$SCRIPT_DIR/knowledge.sql"

    echo ""
    echo "Seed data loaded:"
    sqlite3 "$DB_PATH" "SELECT 'tag_taxonomy: ' || COUNT(*) FROM tag_taxonomy;"
    sqlite3 "$DB_PATH" "SELECT 'topic_index: ' || COUNT(*) FROM topic_index;"
    sqlite3 "$DB_PATH" "SELECT 'knowledge_base: ' || COUNT(*) FROM knowledge_base;"

elif [ "$BACKEND" = "postgresql" ]; then
    # Use DATABASE_URL or individual PG* vars

    echo "Loading tag_taxonomy..."
    psql -f "$SCRIPT_DIR/tag_taxonomy.sql"

    echo "Loading topics..."
    psql -f "$SCRIPT_DIR/topics.sql"

    echo "Loading knowledge..."
    psql -f "$SCRIPT_DIR/knowledge.sql"

    echo ""
    echo "Seed data loaded:"
    psql -t -c "SELECT 'tag_taxonomy: ' || COUNT(*) FROM tag_taxonomy;"
    psql -t -c "SELECT 'topic_index: ' || COUNT(*) FROM topic_index;"
    psql -t -c "SELECT 'knowledge_base: ' || COUNT(*) FROM knowledge_base;"

else
    echo "Error: Unknown backend '$BACKEND'"
    echo "Usage: ./run-seeds.sh [sqlite|postgresql] [db_path]"
    exit 1
fi

echo ""
echo "Done!"
