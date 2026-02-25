# Usage

## Command Syntax

```bash
# Auto-select type and style based on content
/baoyu-article-illustrator path/to/article.md

# Specify type
/baoyu-article-illustrator path/to/article.md --type infographic

# Specify style
/baoyu-article-illustrator path/to/article.md --style blueprint

# Combine type and style
/baoyu-article-illustrator path/to/article.md --type flowchart --style notion

# Specify density
/baoyu-article-illustrator path/to/article.md --density rich

# Direct content input (paste mode)
/baoyu-article-illustrator
[paste content]
```

## Options

| Option | Description |
|--------|-------------|
| `--type <name>` | Illustration type (see Type Gallery in SKILL.md) |
| `--style <name>` | Visual style (see references/styles.md) |
| `--density <level>` | Image count: minimal / balanced / rich |

## Input Modes

| Mode | Trigger | Output Directory |
|------|---------|------------------|
| File path | `path/to/article.md` | Use `default_output_dir` preference, or ask if not set |
| Paste content | No path argument | `illustrations/{topic-slug}/` |

## Output Directory Options

| Value | Path |
|-------|------|
| `same-dir` | `{article-dir}/` |
| `illustrations-subdir` | `{article-dir}/illustrations/` |
| `independent` | `illustrations/{topic-slug}/` |

Configure in EXTEND.md: `default_output_dir: illustrations-subdir`

## Examples

**Technical article with data**:
```bash
/baoyu-article-illustrator api-design.md --type infographic --style blueprint
```

**Personal story**:
```bash
/baoyu-article-illustrator journey.md --type scene --style warm
```

**Tutorial with steps**:
```bash
/baoyu-article-illustrator how-to-deploy.md --type flowchart --density rich
```
