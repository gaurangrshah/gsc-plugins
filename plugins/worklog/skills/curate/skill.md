---
name: curate
description: On-demand knowledge base curation - normalize tags, find duplicates, manage topics, promote memories
---

# Knowledge Base Curation Skill

On-demand curation of the worklog knowledge base. Use this skill to maintain knowledge quality and organization.

## Prerequisites

- Worklog plugin configured with PostgreSQL backend
- Curation tables created (INFA-290 migration applied)
- Curation MCP tools available (INFA-291)

## Subcommands

| Command | Purpose |
|---------|---------|
| `/curate topic [name]` | Focus curation on specific topic |
| `/curate duplicates` | Scan and flag potential duplicates |
| `/curate orphans` | Find unlinked entries |
| `/curate taxonomy` | Review and normalize tags |
| `/curate promote` | Evaluate staging memories for promotion |
| `/curate status` | Show curation system status |

---

## /curate topic [name]

Create or update a topic in the topic index, linking relevant entries.

### Workflow

1. **Check if topic exists**
   ```
   Use MCP: query_table(table="topic_index", filter_column="topic_name", filter_value="[name]")
   ```

2. **If new topic - create it**
   ```
   Use MCP: create_topic(topic_name="[name]", summary="[brief description]", key_terms="term1,term2,term3")
   ```

3. **Find relevant entries**
   Search across memories and knowledge_base for entries related to this topic:
   ```
   Use MCP: search_knowledge(query="[name]", tables="memories,knowledge_base,entries", limit=50)
   ```

4. **Present candidates to user**
   ```markdown
   ## Topic: [name]

   ### Candidates for inclusion:

   | # | Source | Title | Relevance |
   |---|--------|-------|-----------|
   | 1 | memories | [key] | HIGH/MEDIUM/LOW |
   | 2 | knowledge_base | [title] | HIGH/MEDIUM/LOW |
   ...

   **Select entries to add (comma-separated numbers, or 'all'):**
   ```

5. **Add selected entries**
   For each selected entry:
   ```
   Use MCP: add_topic_entry(topic_name="[name]", entry_table="[table]", entry_id=[id], relevance_score=[0.0-1.0])
   ```

6. **Update topic summary**
   Generate summary based on linked entries:
   ```
   Use MCP: update_topic_summary(topic_name="[name]", summary="[TLDR]", full_summary="[detailed]", key_terms="[terms]")
   ```

7. **Log curation run**
   ```
   Use MCP: log_curation_run(operation="topic_indexing", agent="claude", stats='{"topic":"[name]","entries_added":N}')
   ```

---

## /curate duplicates

Scan for potential duplicate entries across the knowledge base.

### Workflow

1. **Check pending duplicates**
   ```
   Use MCP: query_table(table="duplicate_candidates", filter_column="status", filter_value="pending", limit=20)
   ```

2. **If pending duplicates exist, present for review**
   ```markdown
   ## Pending Duplicate Candidates

   ### Pair #1 (similarity: 0.85)
   **Entry 1:** [table].[id] - [title/key]
   > [preview of content]

   **Entry 2:** [table].[id] - [title/key]
   > [preview of content]

   **Action:** [merge / dismiss / skip]
   ```

3. **For new scan - detect duplicates**
   Search for entries with similar titles or content:
   ```
   Use MCP: search_knowledge(query="[common terms]", tables="memories,knowledge_base", limit=100)
   ```

   Compare entries using:
   - Title similarity (exact matches, fuzzy matches)
   - Content overlap (shared phrases, concepts)
   - Tag similarity

4. **Record new candidates**
   For each potential duplicate pair found:
   - Check if pair already exists in duplicate_candidates
   - If new, would need direct SQL to insert (future: add_duplicate_candidate MCP tool)

5. **Process user decisions**
   - **merge**: Combine entries, archive duplicate
   - **dismiss**: Mark as not-duplicate, won't show again
   - **skip**: Leave for later review

6. **Log curation run**
   ```
   Use MCP: log_curation_run(operation="duplicate_detection", agent="claude", stats='{"scanned":N,"found":M,"resolved":K}')
   ```

---

## /curate orphans

Find entries with no relationships or topic associations.

### Workflow

1. **Find orphan memories**
   ```sql
   -- Memories not in any topic and with no relationships
   SELECT m.id, m.key, m.summary
   FROM memories m
   WHERE NOT EXISTS (
     SELECT 1 FROM topic_entries te
     WHERE te.entry_table = 'memories' AND te.entry_id = m.id
   )
   AND NOT EXISTS (
     SELECT 1 FROM relationships r
     WHERE (r.source_table = 'memories' AND r.source_id = m.id)
        OR (r.target_table = 'memories' AND r.target_id = m.id)
   )
   AND m.importance >= 5
   ORDER BY m.importance DESC
   LIMIT 20;
   ```

2. **Find orphan knowledge entries**
   ```sql
   SELECT kb.id, kb.title, kb.category
   FROM knowledge_base kb
   WHERE NOT EXISTS (
     SELECT 1 FROM topic_entries te
     WHERE te.entry_table = 'knowledge_base' AND te.entry_id = kb.id
   )
   AND NOT EXISTS (
     SELECT 1 FROM relationships r
     WHERE (r.source_table = 'knowledge_base' AND r.source_id = kb.id)
        OR (r.target_table = 'knowledge_base' AND r.target_id = kb.id)
   )
   ORDER BY kb.updated_at DESC
   LIMIT 20;
   ```

3. **Present orphans for action**
   ```markdown
   ## Orphan Entries

   These entries have no topic associations or relationships.

   ### High-Value Memories (importance >= 7)
   | ID | Key | Summary | Action |
   |----|-----|---------|--------|
   | 42 | ctx_... | [summary] | [link / archive / skip] |

   ### Knowledge Base Entries
   | ID | Title | Category | Action |
   |----|-------|----------|--------|
   | 15 | [title] | development | [link / archive / skip] |

   **Actions:**
   - **link**: Suggest topics/relationships to add
   - **archive**: Mark as archived (low value)
   - **skip**: Leave for later
   ```

4. **Process user decisions**
   - **link**: Prompt for topic name or related entry, then create relationship
   - **archive**: Update memory status to 'archived'
   - **skip**: Continue to next

5. **Log curation run**
   ```
   Use MCP: log_curation_run(operation="orphan_detection", agent="claude", stats='{"orphans_found":N,"linked":M,"archived":K}')
   ```

---

## /curate taxonomy

Review and normalize tag usage across the knowledge base.

### Workflow

1. **Get current tag taxonomy**
   ```
   Use MCP: query_table(table="tag_taxonomy", columns="canonical_tag,aliases,category,usage_count", order_by="usage_count DESC", limit=50)
   ```

2. **Find tags not in taxonomy**
   Scan memories and knowledge_base for tags not in tag_taxonomy:
   ```sql
   -- Get all unique tags from memories
   SELECT DISTINCT unnest(string_to_array(tags, ',')) as tag
   FROM memories WHERE tags IS NOT NULL AND tags != ''
   EXCEPT
   SELECT canonical_tag FROM tag_taxonomy
   EXCEPT
   SELECT unnest(aliases) FROM tag_taxonomy;
   ```

3. **Present unknown tags**
   ```markdown
   ## Tag Taxonomy Review

   ### Current Taxonomy (top 10 by usage)
   | Tag | Category | Aliases | Usage |
   |-----|----------|---------|-------|
   | infrastructure | system | infra, ops | 45 |

   ### Unknown Tags Found
   | Tag | Occurrences | Action |
   |-----|-------------|--------|
   | k8s | 12 | [add / alias / ignore] |
   | kubernetes | 8 | [add / alias / ignore] |

   **Suggestion:** 'k8s' appears to be an alias for 'kubernetes'

   **Actions:**
   - **add**: Add as new canonical tag
   - **alias [tag]**: Add as alias to existing tag
   - **ignore**: Skip this tag
   ```

4. **Process user decisions**
   - **add**:
     ```
     Use MCP: add_tag_taxonomy(canonical_tag="[tag]", category="[category]")
     ```
   - **alias [canonical]**:
     ```
     Update tag_taxonomy to add alias (future: update_tag_taxonomy MCP tool)
     ```
   - **ignore**: Skip

5. **Normalize existing entries**
   For each entry using non-canonical tags:
   ```
   Use MCP: normalize_tags(tags="[current_tags]")
   ```
   Then update the entry with normalized tags.

6. **Log curation run**
   ```
   Use MCP: log_curation_run(operation="tag_normalization", agent="claude", stats='{"tags_reviewed":N,"added":M,"aliased":K}')
   ```

---

## /curate promote

Evaluate staging memories for promotion to permanent status.

### Workflow

1. **Find promotion candidates**
   Memories with:
   - status = 'staging' (not yet promoted)
   - importance >= 6
   - age > 1 day (not too recent)

   ```sql
   SELECT id, key, summary, content, importance, memory_type, tags, created_at
   FROM memories
   WHERE status = 'staging'
     AND importance >= 6
     AND created_at < NOW() - INTERVAL '1 day'
   ORDER BY importance DESC, created_at ASC
   LIMIT 10;
   ```

2. **Present candidates for review**
   ```markdown
   ## Promotion Candidates

   ### Memory #1: [key]
   - **Type:** fact
   - **Importance:** 7
   - **Created:** 2025-12-28
   - **Tags:** infrastructure, deployment

   > [content preview]

   **Decision:** [promote / archive / boost / skip]
   - **promote**: Move to 'promoted' status
   - **archive**: Mark as archived (not valuable)
   - **boost**: Increase importance and promote
   - **skip**: Leave for later
   ```

3. **Process user decisions**
   For each decision:
   - Record in promotion_history
   - Update memory status

   ```
   Use MCP: update_memory(key="[key]", status="promoted", importance=[new_importance])
   ```

   Log to promotion_history (direct SQL):
   ```sql
   INSERT INTO promotion_history (memory_id, from_status, to_status, reason, promoted_by)
   VALUES ([id], 'staging', 'promoted', '[reason]', 'claude');
   ```

4. **Log curation run**
   ```
   Use MCP: log_curation_run(operation="memory_promotion", agent="claude", stats='{"reviewed":N,"promoted":M,"archived":K}')
   ```

---

## /curate status

Show current state of the curation system.

### Workflow

1. **Gather statistics**
   ```
   Use MCP: list_tables()
   ```

   Plus specific counts:
   - Topics: `query_table(table="topic_index", columns="count(*)")`
   - Relationships: `query_table(table="relationships", columns="count(*)")`
   - Pending duplicates: `query_table(table="duplicate_candidates", filter_column="status", filter_value="pending")`
   - Tag taxonomy size: `query_table(table="tag_taxonomy", columns="count(*)")`

2. **Get recent curation history**
   ```
   Use MCP: query_table(table="curation_history", order_by="run_at DESC", limit=5)
   ```

3. **Present status report**
   ```markdown
   ## Curation System Status

   ### Tables
   | Table | Count |
   |-------|-------|
   | topic_index | 12 |
   | topic_entries | 87 |
   | relationships | 45 |
   | duplicate_candidates | 3 pending |
   | tag_taxonomy | 28 |
   | promotion_history | 15 |
   | curation_history | 42 |

   ### Recent Curation Runs
   | When | Operation | Agent | Stats |
   |------|-----------|-------|-------|
   | 2h ago | topic_indexing | claude | 5 entries added |
   | 1d ago | tag_normalization | claude | 3 tags added |

   ### Recommendations
   - 3 pending duplicates need review (`/curate duplicates`)
   - 15 orphan entries found (`/curate orphans`)
   - 8 unknown tags detected (`/curate taxonomy`)
   ```

---

## Summary Report Format

After any curation operation, provide a summary:

```markdown
## Curation Complete

### Operation: [operation_type]
- **Duration:** [X seconds]
- **Items processed:** N
- **Changes made:** M

### Actions Taken
- [List of specific changes]

### Recommendations
- [Follow-up suggestions]

---
*Logged to curation_history*
```

---

## MCP Tools Reference

| Tool | Purpose |
|------|---------|
| `normalize_tag(tag)` | Normalize single tag to canonical form |
| `normalize_tags(tags)` | Normalize comma-separated tags |
| `add_tag_taxonomy(canonical_tag, aliases, category, description)` | Add new canonical tag |
| `add_relationship(source_table, source_id, target_table, target_id, relationship_type, confidence)` | Create entry relationship |
| `get_relationships(entry_table, entry_id, relationship_type, direction)` | Query relationships |
| `create_topic(topic_name, summary, key_terms)` | Create new topic |
| `add_topic_entry(topic_name, entry_table, entry_id, relevance_score)` | Link entry to topic |
| `get_topic_entries(topic_name, entry_table, min_relevance, limit)` | Get entries for topic |
| `update_topic_summary(topic_name, summary, full_summary, key_terms)` | Update topic metadata |
| `log_curation_run(operation, agent, stats, duration_seconds, success, error_message)` | Log curation operation |

---

## Related

- **INFA-290**: Schema migrations (tables created)
- **INFA-291**: MCP tools (tool implementations)
- **INFA-293**: Curator agent (automated curation)
- **Skill**: `/memory-recall` - Query knowledge base
- **Skill**: `/memory-store` - Store new memories
