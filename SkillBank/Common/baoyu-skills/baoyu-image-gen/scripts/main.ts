import path from "node:path";
import process from "node:process";
import { homedir } from "node:os";
import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import type { CliArgs, Provider, ExtendConfig } from "./types";

function printUsage(): void {
  console.log(`Usage:
  npx -y bun scripts/main.ts --prompt "A cat" --image cat.png
  npx -y bun scripts/main.ts --prompt "A landscape" --image landscape.png --ar 16:9
  npx -y bun scripts/main.ts --promptfiles system.md content.md --image out.png

Options:
  -p, --prompt <text>       Prompt text
  --promptfiles <files...>  Read prompt from files (concatenated)
  --image <path>            Output image path (required)
  --provider google|openai|dashscope|replicate  Force provider (auto-detect by default)
  -m, --model <id>          Model ID
  --ar <ratio>              Aspect ratio (e.g., 16:9, 1:1, 4:3)
  --size <WxH>              Size (e.g., 1024x1024)
  --quality normal|2k       Quality preset (default: 2k)
  --imageSize 1K|2K|4K      Image size for Google (default: from quality)
  --ref <files...>          Reference images (Google multimodal or OpenAI edits)
  --n <count>               Number of images (default: 1)
  --json                    JSON output
  -h, --help                Show help

Environment variables:
  OPENAI_API_KEY            OpenAI API key
  GOOGLE_API_KEY            Google API key
  GEMINI_API_KEY            Gemini API key (alias for GOOGLE_API_KEY)
  DASHSCOPE_API_KEY         DashScope API key (阿里云通义万象)
  REPLICATE_API_TOKEN       Replicate API token
  OPENAI_IMAGE_MODEL        Default OpenAI model (gpt-image-1.5)
  GOOGLE_IMAGE_MODEL        Default Google model (gemini-3-pro-image-preview)
  DASHSCOPE_IMAGE_MODEL     Default DashScope model (z-image-turbo)
  REPLICATE_IMAGE_MODEL     Default Replicate model (google/nano-banana-pro)
  OPENAI_BASE_URL           Custom OpenAI endpoint
  GOOGLE_BASE_URL           Custom Google endpoint
  DASHSCOPE_BASE_URL        Custom DashScope endpoint
  REPLICATE_BASE_URL        Custom Replicate endpoint

Env file load order: CLI args > EXTEND.md > process.env > <cwd>/.baoyu-skills/.env > ~/.baoyu-skills/.env`);
}

function parseArgs(argv: string[]): CliArgs {
  const out: CliArgs = {
    prompt: null,
    promptFiles: [],
    imagePath: null,
    provider: null,
    model: null,
    aspectRatio: null,
    size: null,
    quality: null,
    imageSize: null,
    referenceImages: [],
    n: 1,
    json: false,
    help: false,
  };

  const positional: string[] = [];

  const takeMany = (i: number): { items: string[]; next: number } => {
    const items: string[] = [];
    let j = i + 1;
    while (j < argv.length) {
      const v = argv[j]!;
      if (v.startsWith("-")) break;
      items.push(v);
      j++;
    }
    return { items, next: j - 1 };
  };

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

    if (a === "--prompt" || a === "-p") {
      const v = argv[++i];
      if (!v) throw new Error(`Missing value for ${a}`);
      out.prompt = v;
      continue;
    }

    if (a === "--promptfiles") {
      const { items, next } = takeMany(i);
      if (items.length === 0) throw new Error("Missing files for --promptfiles");
      out.promptFiles.push(...items);
      i = next;
      continue;
    }

    if (a === "--image") {
      const v = argv[++i];
      if (!v) throw new Error("Missing value for --image");
      out.imagePath = v;
      continue;
    }

    if (a === "--provider") {
      const v = argv[++i];
      if (v !== "google" && v !== "openai" && v !== "dashscope" && v !== "replicate") throw new Error(`Invalid provider: ${v}`);
      out.provider = v;
      continue;
    }

    if (a === "--model" || a === "-m") {
      const v = argv[++i];
      if (!v) throw new Error(`Missing value for ${a}`);
      out.model = v;
      continue;
    }

    if (a === "--ar") {
      const v = argv[++i];
      if (!v) throw new Error("Missing value for --ar");
      out.aspectRatio = v;
      continue;
    }

    if (a === "--size") {
      const v = argv[++i];
      if (!v) throw new Error("Missing value for --size");
      out.size = v;
      continue;
    }

    if (a === "--quality") {
      const v = argv[++i];
      if (v !== "normal" && v !== "2k") throw new Error(`Invalid quality: ${v}`);
      out.quality = v;
      continue;
    }

    if (a === "--imageSize") {
      const v = argv[++i]?.toUpperCase();
      if (v !== "1K" && v !== "2K" && v !== "4K") throw new Error(`Invalid imageSize: ${v}`);
      out.imageSize = v;
      continue;
    }

    if (a === "--ref" || a === "--reference") {
      const { items, next } = takeMany(i);
      if (items.length === 0) throw new Error(`Missing files for ${a}`);
      out.referenceImages.push(...items);
      i = next;
      continue;
    }

    if (a === "--n") {
      const v = argv[++i];
      if (!v) throw new Error("Missing value for --n");
      out.n = parseInt(v, 10);
      if (isNaN(out.n) || out.n < 1) throw new Error(`Invalid count: ${v}`);
      continue;
    }

    if (a.startsWith("-")) {
      throw new Error(`Unknown option: ${a}`);
    }

    positional.push(a);
  }

  if (!out.prompt && out.promptFiles.length === 0 && positional.length > 0) {
    out.prompt = positional.join(" ");
  }

  return out;
}

async function loadEnvFile(p: string): Promise<Record<string, string>> {
  try {
    const content = await readFile(p, "utf8");
    const env: Record<string, string> = {};
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const idx = trimmed.indexOf("=");
      if (idx === -1) continue;
      const key = trimmed.slice(0, idx).trim();
      let val = trimmed.slice(idx + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      env[key] = val;
    }
    return env;
  } catch {
    return {};
  }
}

async function loadEnv(): Promise<void> {
  const home = homedir();
  const cwd = process.cwd();

  const homeEnv = await loadEnvFile(path.join(home, ".baoyu-skills", ".env"));
  const cwdEnv = await loadEnvFile(path.join(cwd, ".baoyu-skills", ".env"));

  for (const [k, v] of Object.entries(homeEnv)) {
    if (!process.env[k]) process.env[k] = v;
  }
  for (const [k, v] of Object.entries(cwdEnv)) {
    if (!process.env[k]) process.env[k] = v;
  }
}

function extractYamlFrontMatter(content: string): string | null {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*$/m);
  return match ? match[1] : null;
}

function parseSimpleYaml(yaml: string): Partial<ExtendConfig> {
  const config: Partial<ExtendConfig> = {};
  const lines = yaml.split("\n");
  let currentKey: string | null = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    if (trimmed.includes(":") && !trimmed.startsWith("-")) {
      const colonIdx = trimmed.indexOf(":");
      const key = trimmed.slice(0, colonIdx).trim();
      let value = trimmed.slice(colonIdx + 1).trim();

      if (value === "null" || value === "") {
        value = "null";
      }

      if (key === "version") {
        config.version = value === "null" ? 1 : parseInt(value, 10);
      } else if (key === "default_provider") {
        config.default_provider = value === "null" ? null : (value as Provider);
      } else if (key === "default_quality") {
        config.default_quality = value === "null" ? null : (value as "normal" | "2k");
      } else if (key === "default_aspect_ratio") {
        const cleaned = value.replace(/['"]/g, "");
        config.default_aspect_ratio = cleaned === "null" ? null : cleaned;
      } else if (key === "default_image_size") {
        config.default_image_size = value === "null" ? null : (value as "1K" | "2K" | "4K");
      } else if (key === "default_model") {
        config.default_model = { google: null, openai: null, dashscope: null, replicate: null };
        currentKey = "default_model";
      } else if (currentKey === "default_model" && (key === "google" || key === "openai" || key === "dashscope" || key === "replicate")) {
        const cleaned = value.replace(/['"]/g, "");
        config.default_model![key] = cleaned === "null" ? null : cleaned;
      }
    }
  }

  return config;
}

async function loadExtendConfig(): Promise<Partial<ExtendConfig>> {
  const home = homedir();
  const cwd = process.cwd();

  const paths = [
    path.join(cwd, ".baoyu-skills", "baoyu-image-gen", "EXTEND.md"),
    path.join(home, ".baoyu-skills", "baoyu-image-gen", "EXTEND.md"),
  ];

  for (const p of paths) {
    try {
      const content = await readFile(p, "utf8");
      const yaml = extractYamlFrontMatter(content);
      if (!yaml) continue;

      return parseSimpleYaml(yaml);
    } catch {
      continue;
    }
  }

  return {};
}

function mergeConfig(args: CliArgs, extend: Partial<ExtendConfig>): CliArgs {
  return {
    ...args,
    provider: args.provider ?? extend.default_provider ?? null,
    quality: args.quality ?? extend.default_quality ?? null,
    aspectRatio: args.aspectRatio ?? extend.default_aspect_ratio ?? null,
    imageSize: args.imageSize ?? extend.default_image_size ?? null,
  };
}

async function readPromptFromFiles(files: string[]): Promise<string> {
  const parts: string[] = [];
  for (const f of files) {
    parts.push(await readFile(f, "utf8"));
  }
  return parts.join("\n\n");
}

async function readPromptFromStdin(): Promise<string | null> {
  if (process.stdin.isTTY) return null;
  try {
    const t = await Bun.stdin.text();
    const v = t.trim();
    return v.length > 0 ? v : null;
  } catch {
    return null;
  }
}

function normalizeOutputImagePath(p: string): string {
  const full = path.resolve(p);
  const ext = path.extname(full);
  if (ext) return full;
  return `${full}.png`;
}

function detectProvider(args: CliArgs): Provider {
  if (args.referenceImages.length > 0 && args.provider && args.provider !== "google" && args.provider !== "openai" && args.provider !== "replicate") {
    throw new Error(
      "Reference images require a ref-capable provider. Use --provider google (Gemini multimodal), --provider openai (GPT Image edits), or --provider replicate."
    );
  }

  if (args.provider) return args.provider;

  const hasGoogle = !!(process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY);
  const hasOpenai = !!process.env.OPENAI_API_KEY;
  const hasDashscope = !!process.env.DASHSCOPE_API_KEY;
  const hasReplicate = !!process.env.REPLICATE_API_TOKEN;

  if (args.referenceImages.length > 0) {
    if (hasGoogle) return "google";
    if (hasOpenai) return "openai";
    if (hasReplicate) return "replicate";
    throw new Error(
      "Reference images require Google, OpenAI or Replicate. Set GOOGLE_API_KEY/GEMINI_API_KEY, OPENAI_API_KEY, or REPLICATE_API_TOKEN, or remove --ref."
    );
  }

  const available = [hasGoogle && "google", hasOpenai && "openai", hasDashscope && "dashscope", hasReplicate && "replicate"].filter(Boolean) as Provider[];

  if (available.length === 1) return available[0]!;
  if (available.length > 1) return available[0]!;

  throw new Error(
    "No API key found. Set GOOGLE_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, DASHSCOPE_API_KEY, or REPLICATE_API_TOKEN.\n" +
      "Create ~/.baoyu-skills/.env or <cwd>/.baoyu-skills/.env with your keys."
  );
}

async function validateReferenceImages(referenceImages: string[]): Promise<void> {
  for (const refPath of referenceImages) {
    const fullPath = path.resolve(refPath);
    try {
      await access(fullPath);
    } catch {
      throw new Error(`Reference image not found: ${fullPath}`);
    }
  }
}

type ProviderModule = {
  getDefaultModel: () => string;
  generateImage: (prompt: string, model: string, args: CliArgs) => Promise<Uint8Array>;
};

function isRetryableGenerationError(error: unknown): boolean {
  const msg = error instanceof Error ? error.message : String(error);
  const nonRetryableMarkers = [
    "Reference image",
    "not supported",
    "only supported",
    "No API key found",
    "is required",
  ];
  return !nonRetryableMarkers.some((marker) => msg.includes(marker));
}

async function loadProviderModule(provider: Provider): Promise<ProviderModule> {
  if (provider === "google") {
    return (await import("./providers/google")) as ProviderModule;
  }
  if (provider === "dashscope") {
    return (await import("./providers/dashscope")) as ProviderModule;
  }
  if (provider === "replicate") {
    return (await import("./providers/replicate")) as ProviderModule;
  }
  return (await import("./providers/openai")) as ProviderModule;
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printUsage();
    return;
  }

  await loadEnv();
  const extendConfig = await loadExtendConfig();
  const mergedArgs = mergeConfig(args, extendConfig);

  if (!mergedArgs.quality) mergedArgs.quality = "2k";

  let prompt: string | null = mergedArgs.prompt;
  if (!prompt && mergedArgs.promptFiles.length > 0) prompt = await readPromptFromFiles(mergedArgs.promptFiles);
  if (!prompt) prompt = await readPromptFromStdin();

  if (!prompt) {
    console.error("Error: Prompt is required");
    printUsage();
    process.exitCode = 1;
    return;
  }

  if (!mergedArgs.imagePath) {
    console.error("Error: --image is required");
    printUsage();
    process.exitCode = 1;
    return;
  }

  if (mergedArgs.referenceImages.length > 0) {
    await validateReferenceImages(mergedArgs.referenceImages);
  }

  const provider = detectProvider(mergedArgs);
  const providerModule = await loadProviderModule(provider);

  let model = mergedArgs.model;
  if (!model && extendConfig.default_model) {
    if (provider === "google") model = extendConfig.default_model.google ?? null;
    if (provider === "openai") model = extendConfig.default_model.openai ?? null;
    if (provider === "dashscope") model = extendConfig.default_model.dashscope ?? null;
    if (provider === "replicate") model = extendConfig.default_model.replicate ?? null;
  }
  model = model || providerModule.getDefaultModel();

  const outputPath = normalizeOutputImagePath(mergedArgs.imagePath);

  let imageData: Uint8Array;
  let retried = false;

  while (true) {
    try {
      imageData = await providerModule.generateImage(prompt, model, mergedArgs);
      break;
    } catch (e) {
      if (!retried && isRetryableGenerationError(e)) {
        retried = true;
        console.error("Generation failed, retrying...");
        continue;
      }
      throw e;
    }
  }

  const dir = path.dirname(outputPath);
  await mkdir(dir, { recursive: true });
  await writeFile(outputPath, imageData);

  if (mergedArgs.json) {
    console.log(
      JSON.stringify(
        {
          savedImage: outputPath,
          provider,
          model,
          prompt: prompt.slice(0, 200),
        },
        null,
        2
      )
    );
  } else {
    console.log(outputPath);
  }
}

main().catch((e) => {
  const msg = e instanceof Error ? e.message : String(e);
  console.error(msg);
  process.exit(1);
});
