import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import process from "node:process";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";

import { fetchXArticle } from "./graphql.js";
import { formatArticleMarkdown } from "./markdown.js";
import { localizeMarkdownMedia, type LocalizeMarkdownMediaResult } from "./media-localizer.js";
import { hasRequiredXCookies, loadXCookies, refreshXCookies } from "./cookies.js";
import { resolveXToMarkdownConsentPath } from "./paths.js";
import { tweetToMarkdown } from "./tweet-to-markdown.js";

type CliArgs = {
  url: string | null;
  output: string | null;
  json: boolean;
  login: boolean;
  downloadMedia: boolean;
  help: boolean;
};

type ConsentRecord = {
  version: number;
  accepted: boolean;
  acceptedAt: string;
  disclaimerVersion: string;
};

const DISCLAIMER_VERSION = "1.0";

function printUsage(exitCode: number): never {
  const cmd = "npx -y bun skills/baoyu-danger-x-to-markdown/scripts/main.ts";
  console.log(`X (Twitter) to Markdown

Usage:
  ${cmd} <url>
  ${cmd} --url <url>

Options:
  --output <path>, -o  Output path (file or dir). Default: ./x-to-markdown/<slug>/
  --json               Output as JSON
  --download-media     Download images/videos to local ./imgs and ./videos next to markdown
  --login              Refresh cookies only, then exit
  --help, -h           Show help

Examples:
  ${cmd} https://x.com/username/status/1234567890
  ${cmd} https://x.com/i/article/1234567890 -o ./article.md
  ${cmd} https://x.com/username/status/1234567890 -o ./out/
  ${cmd} https://x.com/username/status/1234567890 --download-media
  ${cmd} https://x.com/username/status/1234567890 --json | jq -r '.markdownPath'
  ${cmd} --login
`);
  process.exit(exitCode);
}

function parseArgs(argv: string[]): CliArgs {
  const out: CliArgs = {
    url: null,
    output: null,
    json: false,
    login: false,
    downloadMedia: false,
    help: false,
  };

  const positional: string[] = [];

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;

    if (a === "--help" || a === "-h") {
      out.help = true;
      continue;
    }

    if (a === "--json") {
      out.json = true;
      continue;
    }

    if (a === "--login") {
      out.login = true;
      continue;
    }

    if (a === "--download-media") {
      out.downloadMedia = true;
      continue;
    }

    if (a === "--url") {
      const v = argv[++i];
      if (!v) throw new Error("Missing value for --url");
      out.url = v;
      continue;
    }

    if (a === "--output" || a === "-o") {
      const v = argv[++i];
      if (!v) throw new Error(`Missing value for ${a}`);
      out.output = v;
      continue;
    }

    if (a.startsWith("-")) {
      throw new Error(`Unknown option: ${a}`);
    }

    positional.push(a);
  }

  if (!out.url && positional.length > 0) {
    out.url = positional[0]!;
  }

  return out;
}

function normalizeInputUrl(input: string): string {
  const trimmed = input.trim();
  if (!trimmed) return "";
  try {
    return new URL(trimmed).toString();
  } catch {
    return trimmed;
  }
}

function parseArticleId(input: string): string | null {
  const trimmed = input.trim();
  if (!trimmed) return null;

  try {
    const parsed = new URL(trimmed);
    const match = parsed.pathname.match(/\/(?:i\/)?article\/(\d+)/);
    if (match?.[1]) return match[1];
  } catch {
    return null;
  }

  return null;
}

function parseTweetId(input: string): string | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  if (/^\d+$/.test(trimmed)) return trimmed;

  try {
    const parsed = new URL(trimmed);
    const match = parsed.pathname.match(/\/status(?:es)?\/(\d+)/);
    if (match?.[1]) return match[1];
  } catch {
    return null;
  }

  return null;
}

function parseTweetUsername(input: string): string | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  try {
    const parsed = new URL(trimmed);
    const match = parsed.pathname.match(/^\/([^/]+)\/status(?:es)?\/\d+/);
    if (match?.[1]) return match[1];
  } catch {
    return null;
  }
  return null;
}

function sanitizeSlug(input: string): string {
  return input
    .trim()
    .replace(/^@/, "")
    .replace(/[^a-zA-Z0-9_-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^[-_]+|[-_]+$/g, "")
    .slice(0, 120);
}

function formatBackupTimestamp(date: Date = new Date()): string {
  const pad2 = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}${pad2(date.getMonth() + 1)}${pad2(date.getDate())}-${pad2(date.getHours())}${pad2(
    date.getMinutes()
  )}${pad2(date.getSeconds())}`;
}

async function backupDirIfExists(dir: string, log: (message: string) => void): Promise<void> {
  try {
    if (!fs.existsSync(dir)) return;
    const stat = fs.statSync(dir);
    if (!stat.isDirectory()) return;
    const backup = `${dir}-backup-${formatBackupTimestamp()}`;
    await rename(dir, backup);
    log(`[x-to-markdown] Existing directory moved to: ${backup}`);
  } catch (error) {
    throw new Error(
      `Failed to backup existing directory (${dir}): ${error instanceof Error ? error.message : String(error ?? "")}`
    );
  }
}

function resolveDefaultOutputDir(slug: string): string {
  return path.resolve(process.cwd(), "x-to-markdown", slug);
}

async function resolveOutputPath(
  normalizedUrl: string,
  kind: "tweet" | "article",
  argsOutput: string | null,
  log: (message: string) => void
): Promise<{ outputDir: string; markdownPath: string; slug: string }> {
  const articleId = kind === "article" ? parseArticleId(normalizedUrl) : null;
  const tweetId = kind === "tweet" ? parseTweetId(normalizedUrl) : null;
  const username = kind === "tweet" ? parseTweetUsername(normalizedUrl) : null;

  const userSlug = username ? sanitizeSlug(username) : null;
  const idPart = articleId ?? tweetId ?? String(Date.now());
  const slug = userSlug ?? idPart;

  const defaultFileName = kind === "article" ? `${idPart}.md` : `${idPart}.md`;

  if (argsOutput) {
    const wantsDir = argsOutput.endsWith("/") || argsOutput.endsWith("\\");
    const resolved = path.resolve(argsOutput);
    try {
      if (wantsDir || (fs.existsSync(resolved) && fs.statSync(resolved).isDirectory())) {
        const outputDir = path.join(resolved, slug);
        await backupDirIfExists(outputDir, log);
        await mkdir(outputDir, { recursive: true });
        return { outputDir, markdownPath: path.join(outputDir, defaultFileName), slug };
      }
    } catch {
      // treat as file path
    }

    const outputDir = path.dirname(resolved);
    await mkdir(outputDir, { recursive: true });
    return { outputDir, markdownPath: resolved, slug };
  }

  const outputDir = resolveDefaultOutputDir(slug);
  await backupDirIfExists(outputDir, log);
  await mkdir(outputDir, { recursive: true });
  return { outputDir, markdownPath: path.join(outputDir, defaultFileName), slug };
}

function formatMetaMarkdown(meta: Record<string, string | number | null | undefined>): string {
  const lines = ["---"];
  for (const [key, value] of Object.entries(meta)) {
    if (value === undefined || value === null || value === "") continue;
    if (typeof value === "number") {
      lines.push(`${key}: ${value}`);
    } else {
      lines.push(`${key}: ${JSON.stringify(value)}`);
    }
  }
  lines.push("---");
  return lines.join("\n");
}

async function promptYesNo(question: string): Promise<boolean> {
  if (!process.stdin.isTTY) return false;

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stderr,
  });

  try {
    const answer = await new Promise<string>((resolve) => rl.question(question, resolve));
    const normalized = answer.trim().toLowerCase();
    return normalized === "y" || normalized === "yes";
  } finally {
    rl.close();
  }
}

function isValidConsent(value: unknown): value is ConsentRecord {
  if (!value || typeof value !== "object") return false;
  const record = value as Partial<ConsentRecord>;
  return (
    record.accepted === true &&
    record.disclaimerVersion === DISCLAIMER_VERSION &&
    typeof record.acceptedAt === "string" &&
    record.acceptedAt.length > 0
  );
}

async function ensureConsent(log: (message: string) => void): Promise<void> {
  const consentPath = resolveXToMarkdownConsentPath();

  try {
    if (fs.existsSync(consentPath) && fs.statSync(consentPath).isFile()) {
      const raw = await readFile(consentPath, "utf8");
      const parsed = JSON.parse(raw) as unknown;
      if (isValidConsent(parsed)) {
        log(
          `⚠️  Warning: Using reverse-engineered X API (not official). Accepted on: ${(parsed as ConsentRecord).acceptedAt}`
        );
        return;
      }
    }
  } catch {
    // fall through to prompt
  }

  log(`⚠️  DISCLAIMER

This tool uses a reverse-engineered X (Twitter) API, NOT an official API.

Risks:
- May break without notice if X changes their API
- No official support or guarantees
- Account restrictions possible if API usage detected
- Use at your own risk
`);

  if (!process.stdin.isTTY) {
    throw new Error(
      `Consent required. Run in a TTY or create ${consentPath} with accepted: true and disclaimerVersion: ${DISCLAIMER_VERSION}`
    );
  }

  const accepted = await promptYesNo("Do you accept these terms and wish to continue? (y/N): ");
  if (!accepted) {
    throw new Error("User declined the disclaimer. Exiting.");
  }

  await mkdir(path.dirname(consentPath), { recursive: true });
  const payload: ConsentRecord = {
    version: 1,
    accepted: true,
    acceptedAt: new Date().toISOString(),
    disclaimerVersion: DISCLAIMER_VERSION,
  };
  await writeFile(consentPath, JSON.stringify(payload, null, 2), "utf8");
  log(`[x-to-markdown] Consent saved to: ${consentPath}`);
}

async function convertArticleToMarkdown(
  inputUrl: string,
  articleId: string,
  log: (message: string) => void
): Promise<string> {
  log("[x-to-markdown] Loading cookies...");
  const cookieMap = await loadXCookies(log);
  if (!hasRequiredXCookies(cookieMap)) {
    throw new Error("Missing auth cookies. Provide X_AUTH_TOKEN and X_CT0 or log in via Chrome.");
  }

  log(`[x-to-markdown] Fetching article ${articleId}...`);
  const article = await fetchXArticle(articleId, cookieMap, false);
  const { markdown: body, coverUrl } = formatArticleMarkdown(article);

  const title = typeof (article as any)?.title === "string" ? String((article as any).title).trim() : "";
  const meta = formatMetaMarkdown({
    url: `https://x.com/i/article/${articleId}`,
    requestedUrl: inputUrl,
    title: title || null,
    coverImage: coverUrl,
  });

  return [meta, body.trimEnd()].filter(Boolean).join("\n\n").trimEnd();
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) printUsage(0);
  if (!args.login && !args.url) printUsage(1);

  const log = (message: string) => console.error(message);
  await ensureConsent(log);

  if (args.login) {
    log("[x-to-markdown] Refreshing cookies via browser login...");
    const cookieMap = await refreshXCookies(log);
    if (!hasRequiredXCookies(cookieMap)) {
      throw new Error("Missing auth cookies after login. Please ensure you are logged in to X.");
    }
    log("[x-to-markdown] Cookies refreshed.");
    return;
  }

  const normalizedUrl = normalizeInputUrl(args.url ?? "");
  const articleId = parseArticleId(normalizedUrl);
  const tweetId = parseTweetId(normalizedUrl);
  if (!articleId && !tweetId) {
    throw new Error("Invalid X url. Examples: https://x.com/<user>/status/<id> or https://x.com/i/article/<id>");
  }

  const kind = articleId ? ("article" as const) : ("tweet" as const);
  const { outputDir, markdownPath, slug } = await resolveOutputPath(normalizedUrl, kind, args.output, log);

  let markdown =
    kind === "article" && articleId
      ? await convertArticleToMarkdown(normalizedUrl, articleId, log)
      : await tweetToMarkdown(normalizedUrl, { log });

  let mediaResult: LocalizeMarkdownMediaResult | null = null;

  if (args.downloadMedia) {
    mediaResult = await localizeMarkdownMedia(markdown, {
      markdownPath,
      log,
    });
    markdown = mediaResult.markdown;
    log(
      `[x-to-markdown] Media localized: images=${mediaResult.downloadedImages}, videos=${mediaResult.downloadedVideos}`
    );
  }

  await writeFile(markdownPath, markdown, "utf8");
  log(`[x-to-markdown] Saved: ${markdownPath}`);

  if (args.json) {
    console.log(
      JSON.stringify(
        {
          url: articleId ? `https://x.com/i/article/${articleId}` : normalizedUrl,
          requestedUrl: normalizedUrl,
          type: kind,
          slug,
          outputDir,
          markdownPath,
          downloadMedia: args.downloadMedia,
          downloadedImages: mediaResult?.downloadedImages ?? 0,
          downloadedVideos: mediaResult?.downloadedVideos ?? 0,
          imageDir: mediaResult?.imageDir ?? null,
          videoDir: mediaResult?.videoDir ?? null,
        },
        null,
        2
      )
    );
  } else {
    console.log(markdownPath);
  }
}

await main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error ?? ""));
  process.exit(1);
});
