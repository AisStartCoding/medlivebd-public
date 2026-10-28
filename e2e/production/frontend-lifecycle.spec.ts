/** Credential-owned tracking reads and their navigation lifetime (FR-PAT-46, FR-SEC-08). */
import { expect, test, type Request } from '@playwright/test';

const PATIENT = 'http://localhost:3000';
const path = '**/api/v1/emergency/track/synthetic-lifecycle-token';
const status = (state: string) => ({
  id: 'synthetic-case',
  state,
  problem: 'burn',
  serverTs: new Date().toISOString(),
  inboundAt: new Date().toISOString(),
  inboundEtaMinutes: null,
  declineReason: null,
  hospital: {
    nameBn: 'ডেমো হাসপাতাল',
    nameEn: 'Synthetic Hospital',
    emergencyPhone: null,
    lat: null,
    lng: null,
  },
});

test('an absent tracking credential has a usable invalid-link screen', async ({ page }) => {
  await page.goto(`${PATIENT}/emergency/onway`);
  await expect(page.getByTestId('onway-invalid')).toBeVisible();
  await expect(page.getByTestId('onway-loading')).toBeHidden();
  await expect(page.getByTestId('onway-invalid').getByRole('link')).toHaveAttribute(
    'href',
    '/emergency',
  );
});

test('a slow tracking read keeps its loading state and does not overlap the next poll', async ({
  page,
}) => {
  const pending = new Set<Request>();
  let release: () => void = () => undefined;
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(path, async (route) => {
    pending.add(route.request());
    await held;
    await route.fulfill({ json: { ok: true, data: status('inbound') } }).catch((error: unknown) => {
      if (route.request().failure() === null) throw error;
    });
  });
  page.on('requestfailed', (request) => pending.delete(request));
  await page.clock.install();
  await page.goto(`${PATIENT}/emergency/onway?t=synthetic-lifecycle-token`);
  await expect.poll(() => pending.size).toBe(1);
  await expect(page.getByTestId('onway-loading')).toBeVisible();
  await page.clock.fastForward(10_000);
  // Strict Mode may abort its first mount; only concurrent live reads count.
  expect([...pending].filter((request) => request.failure() === null)).toHaveLength(1);
  release();
  await expect(page.getByTestId('onway-status')).toHaveAttribute('data-state', 'inbound');
  await page.evaluate(() => history.pushState(null, '', '/emergency/onway'));
  await expect(page.getByTestId('onway-invalid')).toBeVisible();
  await expect(page.getByTestId('onway-status')).toBeHidden();
});

test('a read already in flight cannot overwrite a confirmed cancellation', async ({ page }) => {
  let reads = 0;
  let holdPoll = false;
  let release: () => void = () => undefined;
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(path, async (route) => {
    reads += 1;
    if (holdPoll) await held;
    await route.fulfill({ json: { ok: true, data: status('inbound') } }).catch(() => undefined);
  });
  await page.route(`${path}/cancel`, (route) =>
    route.fulfill({ json: { ok: true, data: status('cancelled') } }),
  );
  await page.clock.install();
  await page.goto(`${PATIENT}/emergency/onway?t=synthetic-lifecycle-token`);
  await expect(page.getByTestId('onway-status')).toHaveAttribute('data-state', 'inbound');
  const initialReads = reads;
  holdPoll = true;
  await page.clock.fastForward(5_000);
  await expect.poll(() => reads).toBe(initialReads + 1);
  const beforeCancel = reads;
  await page.getByTestId('onway-cancel').click();
  await page.getByTestId('onway-cancel-confirm').click();
  await expect(page.getByTestId('onway-status')).toHaveAttribute('data-state', 'cancelled');
  release();
  await page.clock.fastForward(10_000);
  await expect(page.getByTestId('onway-status')).toHaveAttribute('data-state', 'cancelled');
  expect(reads).toBe(beforeCancel);
});
