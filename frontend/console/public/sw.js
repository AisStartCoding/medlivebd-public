/** Neutral shell and immutable assets only (FR-OFF-01/03, FR-SEC-08).
 * API, sockets, RSC, credentials, uploads and private documents never enter Cache Storage.
 * The root document is an explicit offline-only exception to HTTP no-store: the
 * server marks its anonymous CSR shell, and its original CSP nonce stays with it.
 */
const PREFIX = 'medlivebd-console-shell-';
const SHELL = PREFIX + 'v2';
const MARKER = 'console-v2';
const CONSOLE = true;
const LEGACY = 'console-shell-v1';
const UI_QUERY = new Set(['session', 'view', 'login', 'tab']);
const MAX_WARM = 128;
const MAX_ENTRIES = 192;

function shellUrl(url) {
  return (
    url.origin === self.location.origin &&
    url.pathname === '/' &&
    (url.search === '' ||
      (CONSOLE && [...url.searchParams.keys()].every((key) => UI_QUERY.has(key))))
  );
}

function assetUrl(url) {
  if (url.origin !== self.location.origin) return false;
  if ([...url.searchParams.keys()].some((key) => key !== 'v')) return false;
  return (
    /^\/_next\/static\/.+\.(?:js|css|woff2?|ttf|png|webp|svg)$/.test(url.pathname) ||
    (url.search === '' && ['/icon.svg', '/manifest.webmanifest'].includes(url.pathname))
  );
}

function representation(request, url) {
  return (
    request.method === 'GET' &&
    !request.headers.has('authorization') &&
    !request.headers.has('rsc') &&
    !request.headers.has('next-router-state-tree') &&
    !url.searchParams.has('_rsc')
  );
}

function assetKey(url) {
  // Only known static assets accept the development build's cache-busting v.
  return new URL(url.pathname, self.location.origin).href;
}

async function keep(cache, key, response, shell) {
  if (!response.ok || response.type !== 'basic' || response.redirected) return false;
  const type = response.headers.get('content-type') ?? '';
  const control = response.headers.get('cache-control') ?? '';
  if (shell) {
    if (!type.includes('text/html') || response.headers.get('x-medlive-offline-shell') !== MARKER)
      return false;
  } else if (/no-store|private/i.test(control) || /text\/html|text\/x-component/i.test(type))
    return false;
  await cache.put(key, response.clone());
  const keys = await cache.keys();
  const assets = keys.filter((entry) => new URL(entry.url).pathname !== '/');
  for (const entry of assets.slice(0, Math.max(0, keys.length - MAX_ENTRIES)))
    await cache.delete(entry);
  return true;
}

self.addEventListener('install', (event) => {
  // Updates wait for existing clients to close. Never reload an active shift.
  event.waitUntil(
    (async () => {
      const cache = await caches.open(SHELL);
      try {
        await keep(cache, '/', await fetch('/'), true);
      } catch {
        /* Retry through warm/navigation. */
      }
    })(),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      for (const key of await caches.keys()) {
        if ((key.startsWith(PREFIX) && key !== SHELL) || key === LEGACY) await caches.delete(key);
      }
      await self.clients.claim();
    })(),
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (!representation(request, url)) return;
  const asset = assetUrl(url);
  const shell = request.mode === 'navigate' && shellUrl(url);
  if (!asset && !shell) return;
  event.respondWith(
    (async () => {
      const cache = await caches.open(SHELL);
      const key = asset ? assetKey(url) : '/';
      try {
        const response = await fetch(request);
        // Never persist a query-bearing document. Its offline fallback is the
        // separately fetched, marked root, whose client reads the current URL.
        if (asset || url.search === '') await keep(cache, key, response, shell);
        return response;
      } catch (error) {
        const cached = await cache.match(key);
        if (cached !== undefined) return cached;
        throw error;
      }
    })(),
  );
});

self.addEventListener('message', (event) => {
  const data = event.data;
  if (
    data?.type !== 'warm' ||
    !Array.isArray(data.urls) ||
    data.urls.length > 512 ||
    typeof data.id !== 'string' ||
    data.id.length > 80
  )
    return;
  const source = event.source;
  if (!source || new URL(source.url).origin !== self.location.origin) return;
  event.waitUntil(
    (async () => {
      const cache = await caches.open(SHELL);
      const urls = [
        ...new Set(
          data.urls
            .filter((raw) => typeof raw === 'string')
            .flatMap((raw) => {
              try {
                const url = new URL(raw, self.location.origin);
                return assetUrl(url) ? [assetKey(url)] : [];
              } catch {
                return [];
              }
            }),
        ),
      ];
      const bounded = urls.slice(0, MAX_WARM);
      let complete = urls.length <= MAX_WARM;
      try {
        complete = (await keep(cache, '/', await fetch('/'), true)) && complete;
      } catch {
        complete = false;
      }
      // Four requests at a time: first paint and clinical writes retain bandwidth.
      for (let i = 0; i < bounded.length; i += 4) {
        const outcomes = await Promise.all(
          bounded.slice(i, i + 4).map(async (url) => {
            try {
              return await keep(cache, url, await fetch(url), false);
            } catch {
              return false;
            }
          }),
        );
        complete = outcomes.every(Boolean) && complete;
      }
      source.postMessage({ type: 'warmed', id: data.id, ready: complete && bounded.length > 0 });
    })(),
  );
});
