# Flattened Python backend follow-up

1. Move domain owners to `backend/<domain>` and group technical helpers beneath
   `backend/core/`; settings live at `backend/core/settings.py`.
2. Rewrite imports and dynamic route references; retire the Node API and workers.
   Preserve test-only reference code and the Django bridge under `testing/`.
3. Port operator command entry points to the existing Python services. Update
   launchers, Python environment, workspaces, CI, Docker and browser test commands.
4. Verify native safety/parity/layering, operator dispatch, selected HTTP contracts,
   shared/UI/schema checks, production browser workflows and local preview startup.
5. Keep source rollback in Git and ignored old runtime directories locally; no schema
   change, database reset outside dedicated test databases or deployment is required.

The following is the completed plan from the earlier modularization checkpoint.

# Backend implementation plan

The downloaded brief is preserved in ../refactor/briefs/BACKEND.md. Every stage
preserves existing paths, HTTP methods, envelope/casing, status/error codes, roles,
RLS, idempotency and transaction/event order. No ORM migrations, provider activation
or public deployment is authorized by this refactor.

1. Clock consistency: online queue arrival controller -> session repository clock;
   retain explicit historical/offline arrival payloads. Add skew regressions for
   both API runtimes, and deterministic database-time fixtures/retry assertions.
   No schema change. Rollback: revert the correctness commit. Gate: queue/standby,
   notification and chronology suites plus Python safety.
2. Catalog slice: routes/controllers/services/repositories for discovery ->
   modules/catalog, with thin SQL-backed GenericAPIView and explicit serializers.
   Existing pipeline remains the sole HTTP/security entry. Gate: route table,
   discovery contracts, invalid filters, scope and bounded SQL growth.
3. Apply the proven ownership map to the remaining existing domains. Rewrite
   imports/callers, including test instrumentation; never copy implementations.
   Keep only genuinely shared technical/domain/transport/provider foundations.
   Gate each checkpoint with compile/import/layering and focused API checks.
4. Instrument scoped request SQL count/duration and response bytes without logging
   SQL values, identifiers or secrets. Measure representative cold reads and inspect
   existing indexes before proposing any migration. Do not cache live/private data
   to manufacture a lower query count. No Redis or ORM dependency is required.
5. Run Node verification, Python safety/parity, supported cross-runtime contracts,
   full production and affected development/built browser gates. Document measured
   outcomes and any justified optional improvements in VALIDATION.md.

Each stage is committed separately on refactor/medlivebd-foundation. Compatibility
imports are temporary only for identified callers; final ownership is recorded in
the module map. The new private repository is created/pushed only after validation.

Checkpoints: clock consistency `86af592`; domain/DRF/SQL diagnostics `9719bba`.
Both preserve SQL migration ownership. Full core and browser acceptance evidence
is recorded separately so a focused checkpoint is never mistaken for all gates.
