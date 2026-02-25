# Detailed Workflow Procedures

## Step 1: Pre-check

### 1.0 Detect & Save Reference Images ⚠️ REQUIRED if images provided

Check if user provided reference images. Handle based on input type:

| Input Type | Action |
|------------|--------|
| Image file path provided | Copy to `references/` subdirectory → can use `--ref` |
| Image in conversation (no path) | **ASK user for file path** with AskUserQuestion |
| User can't provide path | Extract style/palette verbally → append to prompts (NO frontmatter references) |

**CRITICAL**: Only add `references` to prompt frontmatter if files are ACTUALLY SAVED to `references/` directory.

**If user provides file path**:
1. Copy to `references/NN-ref-{slug}.png`
2. Create description: `references/NN-ref-{slug}.md`
3. Verify files exist before proceeding

**If user can't provide path** (extracted verbally):
1. Analyze image visually, extract: colors, style, composition
2. Create `references/extracted-style.md` with extracted info
3. DO NOT add `references` to prompt frontmatter
4. Instead, append extracted style/colors directly to prompt text

**Description File Format** (only when file saved):
```yaml
---
ref_id: NN
filename: NN-ref-{slug}.png
---
[User's description or auto-generated description]
```

**Verification** (only for saved files):
```
Reference Images Saved:
- 01-ref-{slug}.png ✓ (can use --ref)
- 02-ref-{slug}.png ✓ (can use --ref)
```

**Or for extracted style**:
```
Reference Style Extracted (no file):
- Colors: #E8756D coral, #7ECFC0 mint...
- Style: minimal flat vector, clean lines...
→ Will append to prompt text (not --ref)
```

---

### 1.1 Determine Input Type

| Input | Output Directory | Next |
|-------|------------------|------|
| File path | Ask user (1.2) | → 1.2 |
| Pasted content | `illustrations/{topic-slug}/` | → 1.4 |

**Backup rule for pasted content**: If `source.md` exists in target directory, rename to `source-backup-YYYYMMDD-HHMMSS.md` before saving.

### 1.2-1.4 Configuration (file path input only)

Check preferences and existing state, then ask ALL needed questions in ONE AskUserQuestion call (max 4 questions).

**Questions to include** (skip if preference exists or not applicable):

| Question | When to Ask | Options |
|----------|-------------|---------|
| Output directory | No `default_output_dir` in EXTEND.md | `{article-dir}/`, `{article-dir}/imgs/` (Recommended), `{article-dir}/illustrations/`, `illustrations/{topic-slug}/` |
| Existing images | Target dir has `.png/.jpg/.webp` files | `supplement`, `overwrite`, `regenerate` |
| Article update | Always (file path input) | `update`, `copy` |

**Preference Values** (if configured, skip asking):

| `default_output_dir` | Path |
|----------------------|------|
| `same-dir` | `{article-dir}/` |
| `imgs-subdir` | `{article-dir}/imgs/` |
| `illustrations-subdir` | `{article-dir}/illustrations/` |
| `independent` | `illustrations/{topic-slug}/` |

### 1.5 Load Preferences (EXTEND.md) ⛔ BLOCKING

**CRITICAL**: If EXTEND.md not found, MUST complete first-time setup before ANY other questions or steps. Do NOT proceed to reference images, do NOT ask about content, do NOT ask about type/style — ONLY complete the preferences setup first.

```bash
test -f .baoyu-skills/baoyu-article-illustrator/EXTEND.md && echo "project"
test -f "$HOME/.baoyu-skills/baoyu-article-illustrator/EXTEND.md" && echo "user"
```

| Result | Action |
|--------|--------|
| Found | Read, parse, display summary → Continue |
| Not found | ⛔ **BLOCKING**: Run first-time setup ONLY ([config/first-time-setup.md](config/first-time-setup.md)) → Complete and save EXTEND.md → Then continue |

**Supports**: Watermark | Preferred type/style | Custom styles | Language | Output directory

---

## Step 2: Setup & Analyze

### 2.1 Analyze Content

| Analysis | Description |
|----------|-------------|
| Content type | Technical / Tutorial / Methodology / Narrative |
| Illustration purpose | information / visualization / imagination |
| Core arguments | 2-5 main points to visualize |
| Visual opportunities | Positions where illustrations add value |
| Recommended type | Based on content signals and purpose |
| Recommended density | Based on length and complexity |

### 2.2 Extract Core Arguments

- Main thesis
- Key concepts reader needs
- Comparisons/contrasts
- Framework/model proposed

**CRITICAL**: If article uses metaphors (e.g., "电锯切西瓜"), do NOT illustrate literally. Visualize the **underlying concept**.

### 2.3 Identify Positions

**Illustrate**:
- Core arguments (REQUIRED)
- Abstract concepts
- Data comparisons
- Processes, workflows

**Do NOT Illustrate**:
- Metaphors literally
- Decorative scenes
- Generic illustrations

### 2.4 Analyze Reference Images (if provided in Step 1.0)

For each reference image:

| Analysis | Description |
|----------|-------------|
| Visual characteristics | Style, colors, composition |
| Content/subject | What the reference depicts |
| Suitable positions | Which sections match this reference |
| Style match | Which illustration types/styles align |
| Usage recommendation | `direct` / `style` / `palette` |

| Usage | When to Use |
|-------|-------------|
| `direct` | Reference matches desired output closely |
| `style` | Extract visual style characteristics only |
| `palette` | Extract color scheme only |

---

## Step 3: Confirm Settings ⚠️

**Do NOT skip.** Use ONE AskUserQuestion call with max 4 questions. **Q1, Q2, Q3 are ALL REQUIRED.**

### Q1: Illustration Type ⚠️ REQUIRED
- [Recommended based on analysis] (Recommended)
- infographic / scene / flowchart / comparison / framework / timeline / mixed

### Q2: Density ⚠️ REQUIRED - DO NOT SKIP
- minimal (1-2) - Core concepts only
- balanced (3-5) - Major sections
- per-section - At least 1 per section/chapter (Recommended)
- rich (6+) - Comprehensive coverage

### Q3: Style ⚠️ REQUIRED (ALWAYS ask, even with preferred_style in EXTEND.md)

If EXTEND.md has `preferred_style`:
- [Custom style name + brief description] (Recommended)
- [Top compatible core style 1]
- [Top compatible core style 2]
- Other (see full Style Gallery)

If no `preferred_style` (present Core Styles first):
- [Best compatible core style] (Recommended)
- [Other compatible core style 1]
- [Other compatible core style 2]
- Other (see full Style Gallery)

**Core Styles** (simplified selection):

| Core Style | Best For |
|------------|----------|
| `minimal-flat` | General, knowledge sharing, SaaS |
| `sci-fi` | AI, frontier tech, system design |
| `hand-drawn` | Relaxed, reflective, casual |
| `editorial` | Processes, data, journalism |
| `scene` | Narratives, emotional, lifestyle |

Style selection based on Type × Style compatibility matrix (styles.md).
Full specs: `styles/<style>.md`

### Q4: Image Text Language ⚠️ REQUIRED when article language ≠ EXTEND.md `language`

Detect article language from content. If different from EXTEND.md `language` setting, MUST ask:
- Article language (match article content) (Recommended)
- EXTEND.md language (user's general preference)

**Skip only if**: Article language matches EXTEND.md `language`, or EXTEND.md has no `language` setting.

### Display Reference Usage (if references detected in Step 1.0)

When presenting outline preview to user, show reference assignments:

```
Reference Images:
| Ref | Filename | Recommended Usage |
|-----|----------|-------------------|
| 01 | 01-ref-diagram.png | direct → Illustration 1, 3 |
| 02 | 02-ref-chart.png | palette → Illustration 2 |
```

---

## Step 4: Generate Outline

Save as `outline.md`:

```yaml
---
type: infographic
density: balanced
style: blueprint
image_count: 4
references:                    # Only if references provided
  - ref_id: 01
    filename: 01-ref-diagram.png
    description: "Technical diagram showing system architecture"
  - ref_id: 02
    filename: 02-ref-chart.png
    description: "Color chart with brand palette"
---

## Illustration 1

**Position**: [section] / [paragraph]
**Purpose**: [why this helps]
**Visual Content**: [what to show]
**Type Application**: [how type applies]
**References**: [01]                    # Optional: list ref_ids used
**Reference Usage**: direct             # direct | style | palette
**Filename**: 01-infographic-concept-name.png

## Illustration 2
...
```

**Requirements**:
- Each position justified by content needs
- Type applied consistently
- Style reflected in descriptions
- Count matches density
- References assigned based on Step 2.4 analysis

---

## Step 5: Generate Images

### 5.1 Create Prompts ⛔ BLOCKING

**Every illustration MUST have a saved prompt file before generation begins. DO NOT skip this step.**

For each illustration in the outline:

1. **Create prompt file**: `prompts/NN-{type}-{slug}.md`
2. **Include YAML frontmatter**:
   ```yaml
   ---
   illustration_id: 01
   type: infographic
   style: custom-flat-vector
   ---
   ```
3. **Follow type-specific template** from [prompt-construction.md](prompt-construction.md)
4. **Prompt quality requirements** (all REQUIRED):
   - `Layout`: Describe overall composition (grid / radial / hierarchical / left-right / top-down)
   - `ZONES`: Describe each visual area with specific content, not vague descriptions
   - `LABELS`: Use **actual numbers, terms, metrics, quotes from the article** — NOT generic placeholders
   - `COLORS`: Specify hex codes with semantic meaning (e.g., `Coral (#E07A5F) for emphasis`)
   - `STYLE`: Describe line treatment, texture, mood, character rendering
   - `ASPECT`: Specify ratio (e.g., `16:9`)
5. **Apply defaults**: composition requirements, character rendering, text guidelines, watermark
6. **Backup rule**: If prompt file exists, rename to `prompts/NN-{type}-{slug}-backup-YYYYMMDD-HHMMSS.md`

**Verification** ⛔: Before proceeding to 5.2, confirm ALL prompt files exist:
```
Prompt Files:
- prompts/01-infographic-overview.md ✓
- prompts/02-infographic-distillation.md ✓
...
```

**DO NOT** pass ad-hoc inline text to `--prompt` without first saving prompt files. The generation command should either use `--promptfiles prompts/NN-{type}-{slug}.md` or read the saved file content for `--prompt`.

**CRITICAL - References in Frontmatter**:
- Only add `references` field if files ACTUALLY EXIST in `references/` directory
- If style/palette was extracted verbally (no file), append info to prompt BODY instead
- Before writing frontmatter, verify: `test -f references/NN-ref-{slug}.png`

### 5.2 Select Generation Skill

Check available skills. If multiple, ask user.

### 5.3 Process References ⚠️ REQUIRED if references saved in Step 1.0

**DO NOT SKIP if user provided reference images.** For each illustration with references:

1. **VERIFY files exist first**:
   ```bash
   test -f references/NN-ref-{slug}.png && echo "exists" || echo "MISSING"
   ```
   - If file MISSING but in frontmatter → ERROR, fix frontmatter or remove references field
   - If file exists → proceed with processing

2. Read prompt frontmatter for reference info
3. Process based on usage type:

| Usage | Action | Example |
|-------|--------|---------|
| `direct` | Add reference path to `--ref` parameter | `--ref references/01-ref-brand.png` |
| `style` | Analyze reference, append style traits to prompt | "Style: clean lines, gradient backgrounds..." |
| `palette` | Extract colors from reference, append to prompt | "Colors: #E8756D coral, #7ECFC0 mint..." |

4. Check image generation skill capability:

| Skill Supports `--ref` | Action |
|------------------------|--------|
| Yes (e.g., baoyu-image-gen with Google) | Pass reference images via `--ref` |
| No | Convert to text description, append to prompt |

**Verification**: Before generating, confirm reference processing:
```
Reference Processing:
- Illustration 1: using 01-ref-brand.png (direct) ✓
- Illustration 2: extracted palette from 02-ref-style.png ✓
```

### 5.4 Apply Watermark (if enabled)

Add: `Include a subtle watermark "[content]" at [position].`

### 5.5 Generate

1. For each illustration:
   - **Backup rule**: If image file exists, rename to `NN-{type}-{slug}-backup-YYYYMMDD-HHMMSS.md`
   - If references with `direct` usage: include `--ref` parameter
   - Generate image
2. After each: "Generated X/N"
3. On failure: retry once, then log and continue

---

## Step 6: Finalize

### 6.1 Update Article

Insert after corresponding paragraph:
```markdown
![description](illustrations/{slug}/NN-{type}-{slug}.png)
```

Alt text: concise description in article's language.

### 6.2 Output Summary

```
Article Illustration Complete!

Article: [path]
Type: [type] | Density: [level] | Style: [style]
Location: [directory]
Images: X/N generated

Positions:
- 01-xxx.png → After "[Section]"
- 02-yyy.png → After "[Section]"

[If failures]
Failed:
- NN-zzz.png: [reason]
```
