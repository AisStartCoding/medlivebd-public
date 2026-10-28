/** Cold local entry JavaScript bytes; no credentials, API payloads or HAR (NFR-04, FR-SEC-08). */
import { chromium } from '@playwright/test';

const target = new URL(process.argv[2] ?? 'http://localhost:3100');
if (
  !['localhost', '127.0.0.1', '[::1]'].includes(target.hostname) ||
  target.username ||
  target.password ||
  target.search ||
  target.pathname !== '/'
) {
  throw new Error(
    'Measure an unauthenticated local root URL without credentials or query parameters.',
  );
}

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ serviceWorkers: 'block' });
  const responses = [];
  page.on('response', (response) => {
    const url = new URL(response.url());
    if (
      url.origin === target.origin &&
      url.pathname.startsWith('/_next/static/') &&
      url.pathname.endsWith('.js')
    )
      responses.push(response);
  });
  await page.goto(target.href, { waitUntil: 'networkidle' });
  const scripts = await Promise.all(
    responses.map(async (response) => ({
      path: new URL(response.url()).pathname,
      bytes: (await response.body()).length,
    })),
  );
  const unique = [...new Map(scripts.map((script) => [script.path, script])).values()];
  process.stdout.write(
    `${JSON.stringify(
      {
        scriptRequests: unique.length,
        decodedJsBytes: unique.reduce((bytes, script) => bytes + script.bytes, 0),
        scripts: unique,
      },
      null,
      2,
    )}\n`,
  );
} finally {
  await browser.close();
}
