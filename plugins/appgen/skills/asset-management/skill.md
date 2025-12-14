---
name: asset-management
description: Extract, catalog, and propagate reference assets (screenshots, designs) throughout the webgen workflow
version: "1.0"
---

# Asset Management Skill

**Purpose:** Detect, extract, catalog, and propagate reference assets (screenshots, UI mockups, design files) provided by users throughout the entire webgen workflow, ensuring all implementation agents have access to visual references.

## Problem Solved

**Before:** Users provide screenshots or design references in the initial prompt, but these assets:
- Are not cataloged or tracked
- Don't reach architecture/implementation agents
- Get lost in the workflow
- Result in implementations that don't match the reference

**After:** Assets are extracted, cataloged, and made available to every phase of the workflow.

---

## Asset Catalog Structure

### Directory Layout

```
.webgen/
├── assets/
│   ├── catalog.json           # Asset manifest with metadata
│   ├── screenshots/           # UI reference screenshots
│   ├── designs/              # Design files (Figma, Sketch exports)
│   ├── references/           # Other reference materials
│   └── README.md             # Asset usage instructions
```

### Catalog Schema (catalog.json)

```json
{
  "version": "1.0",
  "created": "2024-12-13T10:00:00Z",
  "updated": "2024-12-13T10:00:00Z",
  "projectSlug": "example-project",
  "assets": [
    {
      "id": "asset-1",
      "type": "screenshot",
      "originalName": "hero-reference.png",
      "path": ".webgen/assets/screenshots/hero-reference.png",
      "description": "Hero section layout with gradient background",
      "source": "user-prompt",
      "usedIn": ["architecture", "implementation"],
      "tags": ["hero", "layout", "gradient"],
      "metadata": {
        "width": 1920,
        "height": 1080,
        "format": "png"
      }
    }
  ]
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (asset-1, asset-2, etc.) |
| `type` | string | Asset type: screenshot, design, reference, mockup |
| `originalName` | string | Original filename from user |
| `path` | string | Relative path within project |
| `description` | string | What the asset shows/represents |
| `source` | string | Where it came from: user-prompt, research, generated |
| `usedIn` | array | Which phases need this: requirements, architecture, implementation, etc. |
| `tags` | array | Searchable tags: hero, navigation, footer, layout, color-scheme |
| `metadata` | object | Additional info: dimensions, format, color palette |

---

## Workflow Integration

### Phase 1: Requirements (Asset Extraction)

**When:** User provides `/webgen` command with description

**Action:** Detect and extract assets from the prompt context

**Detection Logic:**
```javascript
// Pseudo-code for asset detection
function detectAssets(prompt, attachments) {
  const assets = [];

  // Check for explicit asset references
  if (prompt.includes("screenshot") || prompt.includes("reference image")) {
    // Asset mentioned
  }

  // Check for file attachments (Claude Code provides these)
  if (attachments && attachments.length > 0) {
    attachments.forEach(file => {
      if (isImageFile(file)) {
        assets.push(createAssetEntry(file));
      }
    });
  }

  // Check shared screenshots location
  const screenshotsDir = "~/workspace/screenshots/";
  // Look for recently added files if user mentioned them

  return assets;
}
```

**Extraction Process:**
1. Scan prompt for asset references
2. Check for file attachments in Claude Code context
3. Check `~/workspace/screenshots/` if user mentioned screenshots
4. Copy assets to `.webgen/assets/{type}/`
5. Generate catalog.json entries
6. Add to orchestrator context for handoff

### Phase 2: Research (Asset Awareness)

**When:** Orchestrator dispatches @webgen for competitive research

**Action:** Make researcher aware of provided assets

**Handoff Context:**
```markdown
## Reference Assets Provided

The following assets were provided for this project:
- **asset-1**: Hero section reference (path: .webgen/assets/screenshots/hero-reference.png)
  - Use to understand desired layout and visual style
  - Tags: hero, layout, gradient

Analyze these assets to inform your competitive research and recommendations.
```

### Phase 3: Architecture (Asset-Driven Decisions)

**When:** Orchestrator dispatches @webgen for project scaffolding

**Action:** Include asset context in architecture decisions

**Handoff Context:**
```markdown
## Architecture Context - Reference Assets

The following reference assets are available:
{{#each assets}}
- **{{id}}**: {{description}}
  - Path: {{path}}
  - Type: {{type}}
  - Relevant for: {{usedIn}}
{{/each}}

**Architecture Guidance:**
- Review reference assets to inform component structure
- Identify components needed based on visual references
- Consider layout patterns shown in screenshots
```

### Phase 4: Implementation (Direct Asset Access)

**When:** Orchestrator dispatches @webgen for code generation

**Action:** Provide direct asset references to implementation agents

**Handoff Context:**
```markdown
## Implementation Assets - CRITICAL

You have access to the following reference assets. **Read and analyze these BEFORE implementing:**

{{#each assets where usedIn includes "implementation"}}
### {{id}}: {{description}}
- **Path:** {{path}}
- **Use for:** {{usedIn}}
- **Tags:** {{tags}}

**MANDATORY:** Use the Read tool to view this asset before implementing related components.
```

**Read Command Example:**
```bash
# Agent should execute:
Read(.webgen/assets/screenshots/hero-reference.png)
# This provides visual context for pixel-perfect implementation
```

### Phase 5: Final (Asset Documentation)

**When:** Final documentation generation

**Action:** Document assets used in the project

**Generated Section (docs/assets.md):**
```markdown
# Reference Assets

This project was generated using the following reference assets:

## Screenshots
- **hero-reference.png**: Hero section layout reference
  - Source: User-provided
  - Used for: Hero component design and layout

## Usage
All reference assets are stored in `.webgen/assets/` for future reference.
```

---

## API: Asset Functions

### extractAssets(prompt, attachments)

**Purpose:** Extract assets from user input and attachments

**Returns:** Array of asset objects

```javascript
{
  id: "asset-1",
  type: "screenshot",
  originalName: "ui-reference.png",
  tempPath: "/tmp/asset-1.png",  // Before copying to project
  description: "Auto-detected from user prompt",
  tags: []
}
```

### createCatalog(projectPath, assets)

**Purpose:** Initialize asset catalog in project

**Actions:**
1. Create `.webgen/assets/` directory structure
2. Copy assets from temp location to project
3. Generate `catalog.json` with metadata
4. Create `README.md` with usage instructions

**Returns:** Path to catalog.json

### loadCatalog(projectPath)

**Purpose:** Load existing catalog for a project

**Returns:** Catalog object with assets array

### addAsset(catalogPath, assetData)

**Purpose:** Add new asset to existing catalog (e.g., from research phase)

**Updates:** catalog.json with new entry and updated timestamp

### getAssetsForPhase(catalogPath, phaseName)

**Purpose:** Filter assets relevant for specific phase

**Returns:** Subset of assets where `usedIn` includes phaseName

---

## Asset Type Detection

### Image Assets

**Extensions:** .png, .jpg, .jpeg, .gif, .webp, .svg

**Analysis:**
- Extract dimensions
- Detect primary colors (for color palette inference)
- Identify UI sections (hero, navigation, footer)

### Design Files

**Extensions:** .fig (Figma export), .sketch (Sketch export), .xd (Adobe XD)

**Note:** These are typically exported as images or PDFs for webgen processing

### Reference Documents

**Extensions:** .pdf (brand guidelines, wireframes)

**Processing:** Extract relevant pages as images if needed

---

## Asset Propagation Protocol

### Orchestrator Responsibility

The **@webgen-orchestrator** must:

1. **Phase 1 (Requirements):** Invoke asset extraction
   ```markdown
   @webgen: Extract any reference assets from the user prompt.
   Use the asset-management skill to create catalog.
   ```

2. **Phase 2+ (All subsequent phases):** Include asset context in dispatch
   ```markdown
   @webgen: Proceeding to [PHASE].

   **Reference Assets Available:**
   - Review catalog at .webgen/assets/catalog.json
   - Read assets before implementing related components

   Load catalog using asset-management skill for full context.
   ```

3. **Handoff verification:** Ensure catalog.json exists before proceeding to implementation

### Agent Responsibility

Each **@webgen** agent invocation must:

1. **Load catalog** at phase start
2. **Read relevant assets** for the current phase
3. **Reference assets** in implementation decisions
4. **Update catalog** if new assets discovered (e.g., from research)

---

## Example Workflow

### User Provides Screenshot

```
User: /webgen restaurant landing page. I want it to look like this:
[Attaches: hero-reference.png]

Description: Modern hero section with large food image and reservation button
```

### Phase 1: Asset Extraction

```
@webgen (Requirements phase):
1. Detect attachment: hero-reference.png
2. Create .webgen/assets/screenshots/hero-reference.png
3. Generate catalog.json:
   {
     "assets": [{
       "id": "asset-1",
       "type": "screenshot",
       "path": ".webgen/assets/screenshots/hero-reference.png",
       "description": "Hero section reference - large food image with reservation button",
       "usedIn": ["architecture", "implementation"],
       "tags": ["hero", "food-image", "cta-button"]
     }]
   }
4. Report to orchestrator: "Asset catalog created with 1 screenshot"
```

### Phase 3: Architecture

```
@webgen (Architecture phase):
1. Load catalog.json
2. Read asset-1 to understand layout requirements
3. Identify components needed: Hero (with image background), CTAButton
4. Include in architecture report: "Hero component based on asset-1 reference"
```

### Phase 4: Implementation

```
@webgen (Implementation phase):
1. Load catalog.json
2. Read .webgen/assets/screenshots/hero-reference.png
3. Analyze:
   - Image fills full viewport height
   - Text overlays image with dark gradient
   - CTA button prominent, centered
   - Color scheme: warm tones (extracted from image)
4. Implement Hero component matching reference
5. Document: "Hero section implements layout from asset-1"
```

---

## Fallbacks and Edge Cases

### No Assets Provided

**Behavior:** Skip asset extraction, proceed normally
**Catalog:** Create empty catalog.json for consistency

```json
{
  "version": "1.0",
  "assets": []
}
```

### Assets Mentioned But Not Attached

**Behavior:** Prompt user to provide the asset

```markdown
You mentioned a screenshot/reference but I don't see an attachment.
Please provide the file, or I can proceed without it using competitive research for design inspiration.
```

### Asset Not Readable

**Behavior:** Log error, continue without asset

```markdown
⚠️ Warning: Could not read asset-1 (hero-reference.png).
Proceeding with competitive research for design guidance instead.
```

### Large Asset Files

**Threshold:** > 10MB

**Behavior:** Store reference in catalog but don't inline in prompts

```markdown
Asset-2 (design-mockup.pdf) is large (15MB).
Stored in catalog for manual reference, but not loaded automatically.
```

---

## Success Criteria

Asset management is successful when:

- [ ] Assets detected from user prompt/attachments
- [ ] Catalog created at `.webgen/assets/catalog.json`
- [ ] Assets copied to appropriate subdirectories
- [ ] Orchestrator includes assets in phase handoffs
- [ ] Architecture agent reviews assets before scaffolding
- [ ] Implementation agents read assets before coding
- [ ] Final documentation includes asset references
- [ ] Asset-driven decisions documented

---

## Integration Checklist

To integrate asset management into webgen:

### Skill Files
- [x] `skills/asset-management/skill.md` (this file)

### Agent Updates
- [ ] `agents/webgen.md` - Add Phase 1 asset extraction
- [ ] `agents/webgen-orchestrator.md` - Add asset propagation

### Command Updates
- [ ] `commands/webgen.md` - Mention asset support in docs

### Documentation
- [ ] `README.md` - Add asset management to features
- [ ] `docs/ARCHITECTURE.md` - Document asset flow

---

## Future Enhancements

1. **Automatic Color Extraction:** Analyze screenshots to extract color palette
2. **Component Detection:** Use AI to identify components in screenshots (hero, nav, footer)
3. **Figma Integration:** Direct import from Figma URLs
4. **Asset Versioning:** Track asset changes across iterations
5. **Multi-Asset Comparison:** Compare multiple reference screenshots

---

**Version:** 1.0
**Created:** 2024-12-13
**Requires:** webgen v1.4+
