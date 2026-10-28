/** The affected Django development flows, one worker and zero retries (FR-SEC-08, NFR-01). */
import { defineConfig } from '@playwright/test';

import base from './playwright.django.config.js';

// This command rebuilds fixtures. Require an explicit disposable database.
const refactorDatabase = process.env['E2E_DATABASE_URL'];
if (refactorDatabase === undefined || !new URL(refactorDatabase).pathname.endsWith('_test')) {
  throw new Error(
    'Set E2E_DATABASE_URL to an explicit local *_test database for the refactor gate.',
  );
}

export default defineConfig({
  ...base,
  testIgnore: ['**/built/**'],
  testMatch: [
    'two-device-queue.spec.ts',
    'guest-booking.spec.ts',
    'doctor-console.spec.ts',
    'lab-report.spec.ts',
    'emergency-burn.spec.ts',
    'ward-board.spec.ts',
    'offline-console.spec.ts',
    'no-show-recovery.spec.ts',
    'gov-dashboard.spec.ts',
    'production/frontend-lifecycle.spec.ts',
  ],
  outputDir: '.local/refactor-test-results',
});
