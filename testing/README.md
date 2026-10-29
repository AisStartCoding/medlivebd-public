# Test tooling outside the Python backend

- `contracts/`: preserved HTTP contract tests, fixture helpers and historical Node
  reference functions used by those assertions. This private workspace has no
  server entry point, start command or deployment target. Its `createApp` is an
  HTTP proxy to the Django test server.
- `django/`: the HTTP bridge, test-provider shims and shared TypeScript queue-vector
  generator used to check Python/domain parity.

These packages exist for regression coverage. The backend runtime is exclusively
Python under `backend/`. Node remains required for Next.js, shared frontend domain
code, SQL migration tooling and these test drivers.

`pnpm test:backend` prepares a dedicated local `_test` database using the configured
owner connection, then runs native Python tests as the restricted application role.
It never rebuilds the development database. `pnpm test:contracts` runs the preserved full compatibility
harness; its ten historical Node-process-spy mismatches have native Python
counterparts and remain explicitly documented in
[the compatibility record](../docs/django-migration/spy-tests.md).

`pnpm test` runs shared/browser units, UI components and schema tests. It no longer
starts the retired Node server. `pnpm verify` includes the native Python suite.
