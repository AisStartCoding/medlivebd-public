import { readFileSync } from 'node:fs';
import vm from 'node:vm';

import { describe, expect, it, vi } from 'vitest';

const origin = 'https://app.test';
const basic = (body, headers = {}) => {
  const response = new Response(body, { headers });
  Object.defineProperty(response, 'type', { value: 'basic' });
  return response;
};

function worker(app) {
  const handlers = new Map();
  const entries = new Map();
  const key = (request) =>
    new URL(typeof request === 'string' ? request : request.url, origin).href;
  const cache = {
    put: async (request, response) => entries.set(key(request), response),
    match: async (request) => entries.get(key(request)),
    keys: async () => [...entries.keys()].map((url) => ({ url })),
    delete: async (request) => entries.delete(key(request)),
  };
  const caches = { open: async () => cache, keys: async () => [], delete: vi.fn() };
  const self = {
    location: { origin },
    clients: { claim: vi.fn() },
    skipWaiting: vi.fn(),
    addEventListener: (type, fn) => handlers.set(type, fn),
  };
  const fetch = vi.fn(async () => basic('asset', { 'content-type': 'application/javascript' }));
  vm.runInNewContext(
    readFileSync(new URL(`../../../../frontend/${app}/public/sw.js`, import.meta.url), 'utf8'),
    { self, caches, URL, fetch },
  );
  const fire = async (type, event = {}) => {
    let pending;
    handlers.get(type)({
      ...event,
      waitUntil: (promise) => {
        pending = promise;
      },
      respondWith: (promise) => {
        pending = promise;
      },
    });
    return await pending;
  };
  const request = (url, headers = {}, mode = 'cors') => ({
    method: 'GET',
    url: new URL(url, origin).href,
    headers: new Headers(headers),
    mode,
  });
  return { fire, request, entries, caches, self, fetch };
}

describe.each(['console', 'patient'])(
  '%s shell privacy and lifecycle (FR-SEC-08, FR-OFF-01)',
  (app) => {
    it('bypasses clinical/API/RSC/token documents and authenticated assets', async () => {
      const w = worker(app);
      for (const request of [
        w.request('/api/v1/me'),
        w.request('/socket.io/'),
        w.request('/documents/report.pdf'),
        w.request('/emergency/onway?t=credential', {}, 'navigate'),
        w.request('/?_rsc=abc', { rsc: '1' }),
        w.request('/_next/static/chunk.js', { authorization: 'Bearer test-only' }),
      ]) {
        expect(await w.fire('fetch', { request })).toBeUndefined();
      }
      expect(w.fetch).not.toHaveBeenCalled();
      expect(w.entries.size).toBe(0);
    });

    it('keeps a marked neutral root with its CSP and uses only that document offline', async () => {
      const w = worker(app);
      const marker = `${app}-${app === 'console' ? 'v2' : 'v3'}`;
      w.fetch.mockResolvedValue(
        basic('<main>neutral</main>', {
          'content-type': 'text/html',
          'cache-control': 'private, no-store',
          'x-medlive-offline-shell': marker,
          'content-security-policy': "script-src 'nonce-test'",
        }),
      );
      await w.fire('fetch', { request: w.request('/', {}, 'navigate') });
      w.fetch.mockRejectedValue(new Error('offline'));
      const answer = await w.fire('fetch', {
        request: w.request(app === 'console' ? '/?view=ward' : '/', {}, 'navigate'),
      });
      expect(answer.headers.get('content-security-policy')).toBe("script-src 'nonce-test'");
      expect(await answer.text()).toBe('<main>neutral</main>');
      expect([...w.entries.keys()]).toEqual([`${origin}/`]);
    });

    it('does not keep a private response or an unmarked document', async () => {
      const w = worker(app);
      w.fetch.mockResolvedValue(
        basic('private', { 'content-type': 'application/javascript', 'cache-control': 'no-store' }),
      );
      await w.fire('fetch', { request: w.request('/_next/static/chunk.js') });
      await w.fire('fetch', { request: w.request('/', {}, 'navigate') });
      expect(w.entries.size).toBe(0);
    });

    it('leaves foreign caches and an active shift alone during installation/update', async () => {
      const w = worker(app);
      const ownOld = `medlivebd-${app}-shell-old`;
      w.caches.keys = async () => [ownOld, 'other-app-cache'];
      await w.fire('install');
      await w.fire('activate');
      expect(w.self.skipWaiting).not.toHaveBeenCalled();
      expect(w.caches.delete).toHaveBeenCalledExactlyOnceWith(ownOld);
    });

    it('does not announce readiness when warmup misses a required asset', async () => {
      const w = worker(app);
      const source = { url: `${origin}/`, postMessage: vi.fn() };
      w.fetch.mockRejectedValue(new Error('offline'));
      await w.fire('message', {
        source,
        data: {
          type: 'warm',
          id: 'test-warm',
          urls: [`${origin}/_next/static/chunk.js`, `${origin}/api/v1/me`],
        },
      });
      expect(source.postMessage).toHaveBeenCalledWith({
        type: 'warmed',
        id: 'test-warm',
        ready: false,
      });
      expect(w.fetch.mock.calls.every(([url]) => !url.includes('/api/'))).toBe(true);
    });
  },
);
