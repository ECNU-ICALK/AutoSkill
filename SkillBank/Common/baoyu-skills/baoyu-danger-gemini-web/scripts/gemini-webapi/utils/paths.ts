import os from 'node:os';
import path from 'node:path';
import process from 'node:process';

const APP_DATA_DIR = 'baoyu-skills';
const GEMINI_DATA_DIR = 'gemini-web';
const COOKIE_FILE_NAME = 'cookies.json';
const PROFILE_DIR_NAME = 'chrome-profile';

export function resolveUserDataRoot(): string {
  if (process.platform === 'win32') {
    return process.env.APPDATA ?? path.join(os.homedir(), 'AppData', 'Roaming');
  }
  if (process.platform === 'darwin') {
    return path.join(os.homedir(), 'Library', 'Application Support');
  }
  return process.env.XDG_DATA_HOME ?? path.join(os.homedir(), '.local', 'share');
}

export function resolveGeminiWebDataDir(): string {
  const override = process.env.GEMINI_WEB_DATA_DIR?.trim();
  if (override) return path.resolve(override);
  return path.join(resolveUserDataRoot(), APP_DATA_DIR, GEMINI_DATA_DIR);
}

export function resolveGeminiWebCookiePath(): string {
  const override = process.env.GEMINI_WEB_COOKIE_PATH?.trim();
  if (override) return path.resolve(override);
  return path.join(resolveGeminiWebDataDir(), COOKIE_FILE_NAME);
}

export function resolveGeminiWebChromeProfileDir(): string {
  const override = process.env.GEMINI_WEB_CHROME_PROFILE_DIR?.trim();
  if (override) return path.resolve(override);
  return path.join(resolveGeminiWebDataDir(), PROFILE_DIR_NAME);
}

export function resolveGeminiWebSessionsDir(): string {
  return path.join(resolveGeminiWebDataDir(), 'sessions');
}

export function resolveGeminiWebSessionPath(name: string): string {
  const sanitized = name.replace(/[^a-zA-Z0-9_-]/g, '_');
  return path.join(resolveGeminiWebSessionsDir(), `${sanitized}.json`);
}

