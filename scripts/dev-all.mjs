/** Run the Python API and the three Next apps from the prepared local environment. */
import { spawn } from 'node:child_process';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const children = ['api', 'patient', 'console', 'site'].map((service) =>
  spawn(process.execPath, [resolve(root, 'scripts/dev-service.mjs'), service], {
    cwd: root,
    env: process.env,
    stdio: 'inherit',
    windowsHide: true,
  }),
);
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  process.exitCode = code;
  for (const child of children) child.kill();
}
for (const child of children) {
  child.on('error', () => stop(1));
  child.on('exit', (code) => stop(code ?? 1));
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
