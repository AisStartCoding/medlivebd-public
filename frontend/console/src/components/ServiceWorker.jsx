'use client';

import { useEffect } from 'react';

/** Register after paint; report readiness only for a completed, correlated warmup (FR-OFF-01). */
export function ServiceWorker() {
  useEffect(() => {
    if (!('serviceWorker' in navigator)) return undefined;
    const workers = navigator.serviceWorker;
    let disposed = false;
    let warmId = null;
    let detachWait = () => {};
    delete document.documentElement.dataset['offlineReady'];
    const onMessage = (event) => {
      const data = event.data;
      if (
        !disposed &&
        event.source === workers.controller &&
        data?.type === 'warmed' &&
        data.id === warmId &&
        data.ready === true
      ) {
        document.documentElement.dataset['offlineReady'] = 'true';
      }
    };
    workers.addEventListener('message', onMessage);
    const start = async () => {
      try {
        await workers.register('/sw.js');
        await workers.ready;
        if (disposed) return;
        if (workers.controller === null) {
          await new Promise((resolve) => {
            const finish = () => {
              clearTimeout(timer);
              workers.removeEventListener('controllerchange', finish);
              resolve();
            };
            const timer = setTimeout(finish, 10_000);
            detachWait = finish;
            workers.addEventListener('controllerchange', finish);
            if (workers.controller !== null) finish();
          });
        }
        if (disposed || workers.controller === null) return;
        const loaded = performance
          .getEntriesByType('resource')
          .map((entry) => entry.name)
          .filter((name) => {
            const url = new URL(name);
            return url.origin === location.origin && url.pathname.startsWith('/_next/static/');
          });
        warmId = crypto.randomUUID();
        workers.controller.postMessage({ type: 'warm', id: warmId, urls: loaded });
      } catch {
        // Offline reload is optional; clinical data and writes have their own stores.
      }
    };
    const onLoad = () => {
      void start();
    };
    if (document.readyState === 'complete') onLoad();
    else globalThis.addEventListener('load', onLoad, { once: true });
    return () => {
      disposed = true;
      detachWait();
      globalThis.removeEventListener('load', onLoad);
      workers.removeEventListener('message', onMessage);
    };
  }, []);
  return null;
}
