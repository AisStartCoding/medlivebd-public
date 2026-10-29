# Backend validation

## Flat Python backend and grouped core — 28 October 2026

This stage follows the owner's explicit request for Django/Python only and domain
folders directly under `backend/`. Settings are `backend/core/settings.py`; shared
helpers are grouped under security, database, HTTP, validation and observability.
The old Django nesting, Node server entry, workers and Node serving commands are
removed. Historical contract assertions/reference helpers and non-Python drivers
are preserved under `testing/`, outside the backend runtime. Operator entry points
now call the canonical Python services. No schema migration or product/UI redesign
was introduced.

Checks actually run:

| Check | Result |
| --- | --- |
| Frozen pnpm install after workspace relocation | Passed; dependency versions retained |
| Workspace typecheck | Passed |
| Explicit browser-fixture TypeScript check | Passed |
| Shared/domain/UI/schema (`pnpm test --maxWorkers=1`) | 6,228/6,228 across 98 files |
| Native backend, including four operator-command regressions | 237/237 |
| Selected Django HTTP contracts, 11 files | 335/335 |
| Django system check and operator CLI help | Passed |
| Full production browser rerun against the same built UIs | 88/88; one worker, zero retries |
| Windows launcher syntax and production-preview restart | Passed |
| Fresh runtime probes | 7/7 API, 8/8 pages; zero page exceptions |

The standalone `pnpm test:backend` path was exercised after adding safe preparation
of its dedicated local `_test` database. The owner connection builds fixtures and
the application role executes the Python tests. The development database on port
5433 was preserved. Shared/schema tests use their separate database. Run database
suites sequentially: an initial concurrent native/HTTP attempt against the same
API test database produced a duplicate-visit fixture error and a native clinical
assertion; both isolated suites passed, without weakening assertions.

The first full production browser run passed 87/88. The reception pilot's end
confirmation closed, but its ended banner was not observed within the existing
10-second assertion. An isolated run passed with HTTP 200 for chamber end, and the
complete rerun passed all 88 with the same production builds. The cause was not
established; no product fix is claimed. Failure-only end-request phase/status
metadata now helps diagnose a recurrence, without recording URLs, IDs, bodies or
tokens. Assertions, timeouts and retry settings are unchanged. Three test-only lab
fetch interceptors also now handle URL inputs, allowing the explicit fixture
TypeScript check to pass.

The full historical 1,936-case compatibility diagnostic was not rerun in this
stage. Its prior ten Node-process-spy limitations remain documented below and in
`docs/django-migration/spy-tests.md`; native Python equivalents pass. The default
`pnpm test` now covers shared/UI/schema projects and `pnpm verify` additionally
runs native Python tests; it no longer starts the retired Node backend.

Docker and Render definitions now target Python; SQL migration tooling has its own
Node image target. No deployment was performed. Docker is unavailable on this
host, so container image builds were not verified. Local Python startup and the
production browser configuration were verified. Rollback is the preceding Git
checkpoint; ignored source archives are retained locally. Generated vectors,
virtual environments, credentials and runtime captures remain ignored.
Browser tests generated 172 design captures; those were archived locally and the
approved tracked reference files restored. This refactor does not replace them.

The earlier checkpoint evidence follows.

Baseline: 8,138/8,148 core cases; 341/344 selected Django contracts; Python 220/220;
production browser 85/85. Ten core failures and three chamber-end failures are
recorded in the local-copy audit and are not the historical Node-only spy cases.

Stage results, query budgets, compatibility and final commands are appended when
run. Database tests use dedicated localhost:5433 *_test databases, never a reset
of healthcare_dev. Node-process spies cannot validate Python: original cases remain
unchanged and Python failure-injection equivalents must pass. No blanket green
claim may hide that distinction.

## Completed stage checks (28 October 2026)

- Clock/chronology focus: 93/93 Node API/schema checks; rerun of API subset 62/62.
- Python safety/parity after the move: 229/229; expanded diagnostics/boundaries
  after final changes: 233/233 (`python -m pytest`).
- Selected Django contracts: 345/345 across 12 files, including queue, tenant,
  booking/retry, demo, clinical, lab, beds, emergency, settings and payments.
- Catalog gate: 11/11 Python checks for route ordering, invalid/repeated filters,
  rejected direct view entry, constant query growth and targeted doctor reads.
- No schema changes: the existing primary key supports doctor lookup.

Same local seeded test DB, same read representation, five warmed trials per action:

| Service read | Before calls / fetched rows / bytes | After calls / fetched rows / bytes | Median before / after |
| --- | --- | --- | --- |
| hospitals limit 1 | 2 / 2 / 2368 | 2 / 2 / 2368 | 7.04 / 7.02 ms |
| hospitals limit 100 (6 hospitals available) | 2 / 11 / 11077 | 2 / 11 / 11077 | 9.53 / 8.05 ms |
| doctor detail | 2 / 46 / 4534 | 2 / 7 / 4534 | 6.03 / 4.49 ms |

The latter changes forty fetched doctors into one, plus six sessions. Local timing
is descriptive, not a production latency promise. Hospital reads were already
batched; their query count stays constant as cards increase. No need for new Redis,
ORM models or indexes was demonstrated. These service counts exclude HTTP/security
and connection scope setup; full request diagnostics report their own scope.

Broader core/build/browser results are recorded below after the runs complete.

Full Node/core verification after the timing fixture correction: `pnpm verify
--maxWorkers=1`, 175 files and 8,164/8,164 cases passed, plus type/lint/format gates.
The expanded run first exposed two exact-hour backup fixture assumptions (29 vs
30 hours and 2 vs 3). The assertion remains exact; the fixture now uses the API
calculator's clock instead of a different machine's database clock. Its focused
six-case readiness rerun passed. No readiness policy was weakened.

Full cross-runtime diagnostic: `pnpm test:django` executed 1,936 cases after the
module move: 1,926 passed and the same 10 Node-process spy cases failed across
six files. There were no additional failures. This command remains a diagnostic,
not a wholly green gate: its in-process Node spies cannot inject/witness Python
transactions. [The exact cases and native equivalents](../django-migration/spy-tests.md)
are retained; the native Python safety/parity suite passed all 233. The separate
selected functional contract gate passed 345/345. None of those ten assertions
was deleted, skipped or weakened; the full Node/core run passed them against Node.

Final workspace build: `pnpm -r --workspace-concurrency=1 --if-present build`
passed for the shared packages, database tooling, Node API/workers, patient,
console and company site. Final post-change typecheck and lint also passed.
Application implementation checkpoint: `367ae0f` (backend checkpoint `9719bba`).

Final launcher verification (28 October 2026): both `-ApiBackend Node` and
`-ApiBackend Django` started successfully with `-Preview -SkipBuild -Background -SkipInstall
-DatabaseProvider Existing`. Each passed **7/7 API** and **8/8 browser-page**
probes, including healthy readiness, public discovery, intended 401 for an
unauthenticated staff request, Socket.IO handshake, patient pages, staff entry
and both company-site languages. No page exceptions, API 500s or failed API
requests were observed. The production-built UI preview with Django is left running in the new copy.
The existing local `healthcare_dev` database on port 5433 was preserved; browser,
API and schema tests used separate disposable test databases.
