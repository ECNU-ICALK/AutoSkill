import type {
  ArticleBlock,
  ArticleContentState,
  ArticleEntity,
  ArticleMediaInfo,
} from "./types.js";

function coerceArticleEntity(value: unknown): ArticleEntity | null {
  if (!value || typeof value !== "object") return null;
  const candidate = value as ArticleEntity;
  if (
    typeof candidate.title === "string" ||
    typeof candidate.plain_text === "string" ||
    typeof candidate.preview_text === "string" ||
    candidate.content_state
  ) {
    return candidate;
  }
  return null;
}

function escapeMarkdownAlt(text: string): string {
  return text.replace(/[\[\]]/g, "\\$&");
}

function normalizeCaption(caption?: string): string {
  const trimmed = caption?.trim();
  if (!trimmed) return "";
  return trimmed.replace(/\s+/g, " ");
}

function resolveMediaUrl(info?: ArticleMediaInfo): string | undefined {
  if (!info) return undefined;
  if (info.original_img_url) return info.original_img_url;
  if (info.preview_image?.original_img_url) return info.preview_image.original_img_url;
  const variants = info.variants ?? [];
  const mp4 = variants
    .filter((variant) => variant?.content_type?.includes("video"))
    .sort((a, b) => (b.bit_rate ?? 0) - (a.bit_rate ?? 0))[0];
  return mp4?.url ?? variants[0]?.url;
}

function buildMediaById(article: ArticleEntity): Map<string, string> {
  const map = new Map<string, string>();
  for (const entity of article.media_entities ?? []) {
    if (!entity?.media_id) continue;
    const url = resolveMediaUrl(entity.media_info);
    if (url) {
      map.set(entity.media_id, url);
    }
  }
  return map;
}

function collectMediaUrls(
  article: ArticleEntity,
  usedUrls: Set<string>,
  excludeUrl?: string
): string[] {
  const urls: string[] = [];
  const addUrl = (url?: string) => {
    if (!url) return;
    if (excludeUrl && url === excludeUrl) {
      usedUrls.add(url);
      return;
    }
    if (usedUrls.has(url)) return;
    usedUrls.add(url);
    urls.push(url);
  };

  for (const entity of article.media_entities ?? []) {
    addUrl(resolveMediaUrl(entity?.media_info));
  }

  return urls;
}

function resolveEntityMediaLines(
  entityKey: number | undefined,
  entityMap: ArticleContentState["entityMap"] | undefined,
  mediaById: Map<string, string>,
  usedUrls: Set<string>
): string[] {
  if (entityKey === undefined || !entityMap) return [];
  const entry = entityMap[String(entityKey)];
  const value = entry?.value;
  if (!value) return [];
  const type = value.type;
  if (type !== "MEDIA" && type !== "IMAGE") return [];

  const caption = normalizeCaption(value.data?.caption);
  const altText = caption ? escapeMarkdownAlt(caption) : "";
  const lines: string[] = [];

  const mediaItems = value.data?.mediaItems ?? [];
  for (const item of mediaItems) {
    const mediaId =
      typeof item?.mediaId === "string"
        ? item.mediaId
        : typeof item?.media_id === "string"
          ? item.media_id
          : undefined;
    const url = mediaId ? mediaById.get(mediaId) : undefined;
    if (url && !usedUrls.has(url)) {
      usedUrls.add(url);
      lines.push(`![${altText}](${url})`);
    }
  }

  const fallbackUrl = typeof value.data?.url === "string" ? value.data.url : undefined;
  if (fallbackUrl && !usedUrls.has(fallbackUrl)) {
    usedUrls.add(fallbackUrl);
    lines.push(`![${altText}](${fallbackUrl})`);
  }

  return lines;
}

function renderContentBlocks(
  blocks: ArticleBlock[],
  entityMap: ArticleContentState["entityMap"] | undefined,
  mediaById: Map<string, string>,
  usedUrls: Set<string>
): string[] {
  const lines: string[] = [];
  let previousKind: "list" | "quote" | "heading" | "text" | "code" | "media" | null = null;
  let listKind: "ordered" | "unordered" | null = null;
  let orderedIndex = 0;
  let inCodeBlock = false;

  const pushBlock = (
    blockLines: string[],
    kind: "list" | "quote" | "heading" | "text" | "media"
  ) => {
    if (blockLines.length === 0) return;
    if (
      lines.length > 0 &&
      previousKind &&
      !(previousKind === kind && (kind === "list" || kind === "quote" || kind === "media"))
    ) {
      lines.push("");
    }
    lines.push(...blockLines);
    previousKind = kind;
  };

  const collectMediaLines = (block: ArticleBlock): string[] => {
    const ranges = Array.isArray(block.entityRanges) ? block.entityRanges : [];
    const mediaLines: string[] = [];
    for (const range of ranges) {
      if (typeof range?.key !== "number") continue;
      mediaLines.push(...resolveEntityMediaLines(range.key, entityMap, mediaById, usedUrls));
    }
    return mediaLines;
  };

  for (const block of blocks) {
    const type = typeof block?.type === "string" ? block.type : "unstyled";
    const text = typeof block?.text === "string" ? block.text : "";

    if (type === "code-block") {
      if (!inCodeBlock) {
        if (lines.length > 0) {
          lines.push("");
        }
        lines.push("```");
        inCodeBlock = true;
      }
      lines.push(text);
      previousKind = "code";
      listKind = null;
      orderedIndex = 0;
      continue;
    }

    if (type === "atomic") {
      if (inCodeBlock) {
        lines.push("```");
        inCodeBlock = false;
        previousKind = "code";
      }
      listKind = null;
      orderedIndex = 0;
      const mediaLines = collectMediaLines(block);
      if (mediaLines.length > 0) {
        pushBlock(mediaLines, "media");
      }
      continue;
    }

    if (inCodeBlock) {
      lines.push("```");
      inCodeBlock = false;
      previousKind = "code";
    }

    if (type === "unordered-list-item") {
      listKind = "unordered";
      orderedIndex = 0;
      pushBlock([`- ${text}`], "list");
      continue;
    }

    if (type === "ordered-list-item") {
      if (listKind !== "ordered") {
        orderedIndex = 0;
      }
      listKind = "ordered";
      orderedIndex += 1;
      pushBlock([`${orderedIndex}. ${text}`], "list");
      continue;
    }

    listKind = null;
    orderedIndex = 0;

    switch (type) {
      case "header-one":
        pushBlock([`# ${text}`], "heading");
        break;
      case "header-two":
        pushBlock([`## ${text}`], "heading");
        break;
      case "header-three":
        pushBlock([`### ${text}`], "heading");
        break;
      case "header-four":
        pushBlock([`#### ${text}`], "heading");
        break;
      case "header-five":
        pushBlock([`##### ${text}`], "heading");
        break;
      case "header-six":
        pushBlock([`###### ${text}`], "heading");
        break;
      case "blockquote": {
        const quoteLines = text.length > 0 ? text.split("\n") : [""];
        pushBlock(quoteLines.map((line) => `> ${line}`), "quote");
        break;
      }
      default:
        pushBlock([text], "text");
        break;
    }

    const trailingMediaLines = collectMediaLines(block);
    if (trailingMediaLines.length > 0) {
      pushBlock(trailingMediaLines, "media");
    }
  }

  if (inCodeBlock) {
    lines.push("```");
  }

  return lines;
}

export type FormatArticleResult = {
  markdown: string;
  coverUrl: string | null;
};

export function formatArticleMarkdown(article: unknown): FormatArticleResult {
  const candidate = coerceArticleEntity(article);
  if (!candidate) {
    return { markdown: `\`\`\`json\n${JSON.stringify(article, null, 2)}\n\`\`\``, coverUrl: null };
  }

  const lines: string[] = [];
  const usedUrls = new Set<string>();
  const mediaById = buildMediaById(candidate);
  const title = typeof candidate.title === "string" ? candidate.title.trim() : "";
  if (title) {
    lines.push(`# ${title}`);
  }

  const coverUrl = resolveMediaUrl(candidate.cover_media?.media_info) ?? null;
  if (coverUrl) {
    usedUrls.add(coverUrl);
  }

  const blocks = candidate.content_state?.blocks;
  const entityMap = candidate.content_state?.entityMap;
  if (Array.isArray(blocks) && blocks.length > 0) {
    const rendered = renderContentBlocks(blocks, entityMap, mediaById, usedUrls);
    if (rendered.length > 0) {
      if (lines.length > 0) lines.push("");
      lines.push(...rendered);
    }
  } else if (typeof candidate.plain_text === "string") {
    if (lines.length > 0) lines.push("");
    lines.push(candidate.plain_text.trim());
  } else if (typeof candidate.preview_text === "string") {
    if (lines.length > 0) lines.push("");
    lines.push(candidate.preview_text.trim());
  }

  const mediaUrls = collectMediaUrls(candidate, usedUrls, coverUrl ?? undefined);
  if (mediaUrls.length > 0) {
    lines.push("", "## Media", "");
    for (const url of mediaUrls) {
      lines.push(`![](${url})`);
    }
  }

  return { markdown: lines.join("\n").trimEnd(), coverUrl };
}
