/**
 * The hospital's own face on its consoles (plan K4; `PRD.md` `FR-BRD-12`;
 * `APP_FLOW.md` B1.1).
 *
 * One read, `GET /hospital/brand`, any member of the hospital's staff: its
 * names, its colours as its patients see them, and its logo as a `data:` URL.
 * Kept for the tab, per hospital, so moving between consoles does not ask
 * again and a console opened offline still wears the brand it last had.
 * Nothing here is a secret; the cache is a convenience, and its absence only
 * means the rail shows the session's name on the platform's colour.
 */

import { ApiClient } from '@platform/client/api';
import { BRAND_TOKENS } from '@platform/domain';

import { API_BASE } from './apiBase';
import { readDemoSession, SESSION_CHANGED } from './demo';

const KEY = 'medlivebd.console.brand.';
const pending = new Map();

globalThis.addEventListener?.(SESSION_CHANGED, () => {
  for (const read of pending.values()) read.controller.abort();
  pending.clear();
});

function kept(hospitalId) {
  try {
    const raw = globalThis.sessionStorage.getItem(KEY + hospitalId);
    return raw === null ? null : JSON.parse(raw);
  } catch {
    return null;
  }
}

function keep(hospitalId, brand) {
  try {
    globalThis.sessionStorage.setItem(KEY + hospitalId, JSON.stringify(brand));
  } catch {
    // A full or blocked store: the next console asks again.
  }
}

/** What this tab already holds for the hospital, without asking. */
export function brandKept(hospitalId) {
  return kept(hospitalId);
}

/** The hospital's face, asked for once per tab. Null when it could not be read. */
export async function loadBrand(hospitalId, token, refresh = false) {
  const already = kept(hospitalId);
  if (!refresh && already !== null) return already;
  const existing = pending.get(hospitalId);
  if (existing?.token === token) return await existing.promise;
  existing?.controller.abort();
  const controller = new AbortController();
  const read = { token, controller, promise: null };
  read.promise = (async () => {
    try {
      const client = new ApiClient({ baseUrl: API_BASE, getToken: () => token });
      const brand = await client.get('/hospital/brand', {
        signal: controller.signal,
        timeoutMs: 10_000,
      });
      const session = readDemoSession();
      if (
        controller.signal.aborted ||
        session?.token !== token ||
        session.hospitalId !== hospitalId
      )
        return null;
      keep(hospitalId, brand);
      return brand;
    } catch {
      return null;
    } finally {
      if (pending.get(hospitalId) === read) pending.delete(hospitalId);
    }
  })();
  pending.set(hospitalId, read);
  return await read.promise;
}

const HEX = /^#[0-9a-fA-F]{6}$/;
const LOGO = /^data:image\/(png|jpeg|webp|svg\+xml);base64,[A-Za-z0-9+/=]+$/;

/** The logo, only if it is the image the API said it would be. */
export function logoOf(brand) {
  return brand?.logo !== null && brand?.logo !== undefined && LOGO.test(brand.logo)
    ? brand.logo
    : null;
}

/**
 * Puts the hospital's colours on the workspace: the six brand tokens on the
 * document, as the patient app does for a portal, so every console reads them
 * and none knows it happened. No theme removes anything set.
 */
export function applyBrand(brand) {
  const root = globalThis.document.documentElement;
  for (const token of BRAND_TOKENS) {
    const value = brand?.theme?.colors[token];
    if (value !== undefined && HEX.test(value)) root.style.setProperty(`--${token}`, value);
    else root.style.removeProperty(`--${token}`);
  }
}
