import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { brandKept, loadBrand } from '../brand.js';
import { writeDemoSession } from '../demo.js';

beforeEach(() => {
  const storage = new Map();
  vi.stubGlobal('sessionStorage', {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
  });
});
afterEach(() => vi.unstubAllGlobals());

describe('scoped branding reads (FR-BRD-12)', () => {
  it('coordinates simultaneous shell/rail reads and reuses only public hospital branding', async () => {
    writeDemoSession({ token: 'test-token-a', hospitalId: 'hospital-a' });
    let release;
    const fetch = vi.fn(
      () =>
        new Promise((resolve) => {
          release = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetch);
    const first = loadBrand('hospital-a', 'test-token-a');
    const second = loadBrand('hospital-a', 'test-token-a');
    expect(fetch).toHaveBeenCalledTimes(1);
    const brand = { nameEn: 'Synthetic hospital A', theme: null, logo: null };
    release(new Response(JSON.stringify({ ok: true, data: brand })));
    expect(await first).toEqual(brand);
    expect(await second).toEqual(brand);
    expect(await loadBrand('hospital-a', 'test-token-a')).toEqual(brand);
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('does not retain a late response after the session identity changes', async () => {
    writeDemoSession({ token: 'old-token', hospitalId: 'hospital-old' });
    let release;
    vi.stubGlobal(
      'fetch',
      () =>
        new Promise((resolve) => {
          release = resolve;
        }),
    );
    const stale = loadBrand('hospital-old', 'old-token');
    writeDemoSession({ token: 'new-token', hospitalId: 'hospital-new' });
    release(new Response(JSON.stringify({ ok: true, data: { nameEn: 'Old synthetic hospital' } })));
    expect(await stale).toBeNull();
    expect(brandKept('hospital-old')).toBeNull();
    expect(brandKept('hospital-new')).toBeNull();
  });
});
