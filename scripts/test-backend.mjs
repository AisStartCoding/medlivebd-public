/** Native backend tests against the existing restricted synthetic test database. */
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
try {
  process.loadEnvFile(resolve(root, '.env'));
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}
const testEnv = {};
for (const line of readFileSync(resolve(root, 'backend/env/test.env'), 'utf8').split(/\r?\n/)) {
  const value = line.trim();
  if (!value || value.startsWith('#') || !value.includes('=')) continue;
  const at = value.indexOf('=');
  testEnv[value.slice(0, at).trim()] = value.slice(at + 1).trim();
}
const testDatabase = new URL(testEnv.DATABASE_URL);
const local = new URL(
  process.env.DATABASE_URL_DJANGO_TEST ??
    process.env.DATABASE_URL ??
    'postgresql://healthcare:healthcare@127.0.0.1:5432/healthcare_django_api_test',
);
if (!['localhost', '127.0.0.1', '[::1]'].includes(local.hostname)) {
  throw new Error('Backend tests require a local database.');
}
if (process.env.DATABASE_URL_DJANGO_TEST) testDatabase.pathname = local.pathname;
if (!testDatabase.pathname.endsWith('_test'))
  throw new Error('Expected a dedicated _test database.');
testDatabase.hostname = '127.0.0.1';
testDatabase.port = local.port;
const ownerDatabase = new URL(local);
ownerDatabase.hostname = '127.0.0.1';
ownerDatabase.pathname = testDatabase.pathname;
const require = createRequire(resolve(root, 'testing/django/package.json'));
const prepared = spawnSync(
  process.execPath,
  [require.resolve('tsx/cli'), resolve(root, 'testing/django/prepare.ts')],
  {
    cwd: root,
    env: { ...process.env, DATABASE_URL_API_TEST: ownerDatabase.toString() },
    stdio: 'inherit',
  },
);
if (prepared.status !== 0) process.exit(prepared.status ?? 1);
const env = {
  ...process.env,
  ...testEnv,
  DATABASE_URL: testDatabase.toString(),
  DJANGO_SETTINGS_MODULE: 'backend.core.test_settings',
};
delete env.DATABASE_URL_OWNER_TEST;
const python = resolve(
  root,
  'backend/.venv',
  process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
);
const result = spawnSync(
  python,
  ['-m', 'pytest', '-c', 'backend/pyproject.toml', 'backend/tests', ...process.argv.slice(2)],
  {
    cwd: root,
    env,
    stdio: 'inherit',
  },
);
process.exit(result.status ?? 1);
