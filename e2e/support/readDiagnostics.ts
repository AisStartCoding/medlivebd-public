/** Bounded technical evidence for a stalled public read, never bodies/credentials (FR-SEC-08). */
import type { Page, Request, TestInfo } from '@playwright/test';

export function observePublicRead(page: Page) {
  const events: { path: string; kind: string; status?: number }[] = [];
  const pending = new Map<Request, string>();
  const pathOf = (request: Request) => {
    const path = new URL(request.url()).pathname;
    return path.startsWith('/_next/static/') || path === '/api/v1/hospitals' || path === '/beds'
      ? path
      : null;
  };
  page.on('request', (request) => {
    const path = pathOf(request);
    if (path !== null) pending.set(request, path);
  });
  page.on('response', (response) => {
    const path = pathOf(response.request());
    if (path !== null && events.length < 100)
      events.push({ path, kind: 'response', status: response.status() });
  });
  page.on('requestfinished', (request) => pending.delete(request));
  page.on('requestfailed', (request) => {
    const path = pathOf(request);
    pending.delete(request);
    if (path !== null && events.length < 100) events.push({ path, kind: 'failed' });
  });
  let pageErrors = 0;
  page.on('pageerror', () => {
    pageErrors += 1;
  });
  return async (info: TestInfo) => {
    const document = await page.evaluate(() => ({
      ready: globalThis.document.readyState,
      loading: globalThis.document.querySelectorAll('[data-testid="beds-loading"]').length,
      failed: globalThis.document.querySelectorAll('[data-testid="beds-failed"]').length,
      cards: globalThis.document.querySelectorAll('[data-testid^="bed-card-"]').length,
      busy: globalThis.document.querySelectorAll('[aria-busy="true"]').length,
      scripts: globalThis.document.scripts.length,
    }));
    await info.attach('public-read-diagnostics', {
      contentType: 'application/json',
      body: JSON.stringify({ document, pageErrors, pending: [...pending.values()], events }),
    });
  };
}
