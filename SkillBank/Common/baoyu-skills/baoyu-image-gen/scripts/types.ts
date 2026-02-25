export type Provider = "google" | "openai" | "dashscope" | "replicate";
export type Quality = "normal" | "2k";

export type CliArgs = {
  prompt: string | null;
  promptFiles: string[];
  imagePath: string | null;
  provider: Provider | null;
  model: string | null;
  aspectRatio: string | null;
  size: string | null;
  quality: Quality | null;
  imageSize: string | null;
  referenceImages: string[];
  n: number;
  json: boolean;
  help: boolean;
};

export type ExtendConfig = {
  version: number;
  default_provider: Provider | null;
  default_quality: Quality | null;
  default_aspect_ratio: string | null;
  default_image_size: "1K" | "2K" | "4K" | null;
  default_model: {
    google: string | null;
    openai: string | null;
    dashscope: string | null;
    replicate: string | null;
  };
};
