# Local-copy verification and comparison — 28 October 2026

The copy is complete and runnable, and its frontend/backend integration works in
the successful flows listed below. **The complete validation is not green:** the
core suite, initial Django contract selection and initial development workflow run
had failures. A clock-skew defect was reproduced. No application code or test
assertion was changed to conceal those results.

The deep automated suites run from `V:\STARTUP\medlivebd`; the original at
`V:\STARTUP\HealthCare` was freshly started and probed separately as the control.
This report separates fresh observations from the
historical evidence in BRANCH_INTEGRATION.md.

## Source and setup comparison

Both checkouts start on master at `0b4d968afe4b9908cd8b8c66109eeb242b7d94a2`,
with Git tree `635b0b4b9cf1d630d81b3ed2747fbb917c750876`.
All **1,729 tracked files (143,514,602 bytes per copy)** were hashed. No file is
missing and no application content differs. BRANCH_INTEGRATION.md has a raw-byte
difference caused only by CRLF/LF line endings; normalized text is identical.
The ignored root .env files were compared without exposing their values and are
identical. This verification report is a new documentation addition to the copy.

The copy originally had source and local configuration but no node_modules or
Python virtual environment. Its own pinned Node dependencies and its own Python
environment have now been installed. No dependency version was upgraded. Existing
demo data was retained; setup found six facilities and applied no new migration.
The tested runtimes are Node 24.19.0 and Python 3.13.2. The frozen Python package
lists in both virtual environments match exactly.

## Fresh original-versus-copy runtime comparison

Each checkout was started separately on ports 3000/3100/3200/4000, using the same
local synthetic demo database. The original was stopped before the copy started;
the browser probes therefore tested the checkout named in their result file.

| Check | Original after fresh start | medlivebd after fresh start |
| --- | --- | --- |
| /healthz | 200, ok | 200, ok |
| /readyz | 200, ready; schema 0063 | 200, ready; schema 0063 |
| Public configuration | 200 | 200 |
| Hospital discovery | 200; 6 facilities | 200; 6 facilities |
| Doctor discovery | 200; 40 doctors | 200; 40 doctors |
| Unauthenticated staff identity | 401 AUTH_REQUIRED | 401 AUTH_REQUIRED |
| Socket.IO polling handshake | 200, valid opening packet | 200, valid opening packet |
| Patient home | 200; rendered, no page errors | 200; rendered, no page errors |
| Patient search | 200; rendered, no page errors | 200; rendered, no page errors |
| Booking entry | 200; rendered, no page errors | 200; rendered, no page errors |
| Beds entry | 200; rendered, no page errors | 200; rendered, no page errors |
| Emergency entry | 200; rendered, no page errors | 200; rendered, no page errors |
| Staff console entry | 200; rendered, no page errors | 200; rendered, no page errors |
| Company site English | 200; rendered, no page errors | 200; rendered, no page errors |
| Company site Bangla | 200; rendered, no page errors | 200; rendered, no page errors |

For these eight pages in both fresh runs, no JavaScript page error, failed API
request or API 5xx was observed during the probe window. This establishes startup,
rendering and basic connectivity, not completion of all workflows. The suites
below test actual actions and persistence on disposable databases.

Raw evidence: [source comparison](../.local/source-comparison.json),
[original runtime](../.local/original-fresh-runtime.json),
[copy runtime](../.local/copy-fresh-runtime.json). Page screenshots are alongside
these files in .local, prefixed original-fresh or copy-fresh. Endpoint timings are
single local observations, not a controlled performance comparison.

## Issue found in the already-running original

The first inspection found old database connection-timeout messages in the
original API log, though the fresh health/readiness/data requests succeeded.
The original's patient search navigation then exceeded 120 seconds while its
Next development server was compiling. Dependency installation was active during
this initial probe, so resource contention is a possible contributor, not a
proven root cause. The partial log is retained as original-before-runtime.log.

After the original's owned services were stopped and freshly started, all seven
backend checks and all eight frontend pages passed. The copy passed the same
checks after its own clean startup. No application-code change was made to obtain
those passes. The initial stall must not be confused with missing copied code or
with proof that the database/API was unavailable throughout.

## Database and permissions

The shared local demo instance is PostgreSQL 16.15 on localhost:5433, database
healthcare_dev. PostGIS 3.4.2, pgcrypto 1.3, cube 1.5 and earthdistance 1.2 are
installed. There are 61 applied ledger entries, with readiness reporting schema
0063. The schema invariant command passed.

All **63 public tables have row-level security enabled**. The launcher connects
the API as healthcare_local_api, whose metadata confirms: no superuser rights,
no database creation, no role creation, no RLS bypass and no CREATE privilege in
the public schema. These metadata checks complement, rather than replace, the
tenant/auth behavior tests. [Database inspection](../.local/database-inspection.json).

Test databases are separate from healthcare_dev: healthcare_copy_node_api_test,
healthcare_copy_schema_test, healthcare_copy_django_api_test and
healthcare_copy_browser_test. Suites may reset those disposable test databases;
the existing demo database is not reset.

## Fresh automated verification

| Check on medlivebd | Fresh result | Evidence |
| --- | --- | --- |
| Frozen install and environment setup | PASS; 594 Node packages installed; Python versions match original exactly | [setup log](../.local/comparison-setup.log), [Python comparison](../.local/python-environment-comparison.json) |
| Workspace types / ESLint / formatting | PASS | [core log](../.local/verify-core.log) |
| Unit/component + Node API + schema | **FAIL: 8,138 passed / 10 failed, 172 files** | [core log](../.local/verify-core.log), [result](../.local/result-core.json) |
| All workspace production builds | PASS, including API/workers and all three Next apps | [build log](../.local/verify-build.log) |
| Selected Django API contracts, 12 files | **FAIL: 341 passed / 3 failed, 344 total** | [Django log](../.local/verify-django.log) |
| Complete queue contract file in isolation | PASS: 35/35; does not erase the initial three failures | [diagnostic log](../.local/queue-end-diagnostic.log) |
| Python safety and queue parity | PASS: 220/220 | [pytest log](../.local/verify-pytest.log) |
| Full production-configuration browser suite, Django | PASS: 85/85 | [production log](../.local/verify-production.log) |
| Selected development workflows, eight specs | **FAIL: 80 passed / 1 failed, 81 total** | [development log](../.local/verify-development.log) |
| Failed emergency case, isolated reproduction attempt | PASS: 1/1, no code/timeout change | [isolated log](../.local/emergency-isolated.log) |
| Built console offline reload, Node API | PASS: 3/3 | [built log](../.local/verify-built.log) |
| Exported bilingual website and accessibility/responsiveness | PASS: 30/30 | [site log](../.local/verify-site.log) |
| Deliberate 1-second API/database clock-skew probe | **Confirmed defect: arrival 200, immediate end 500**; not an acceptance pass | [outcome](../.local/clock-skew-probe-result.json) |
| Standalone smoke, original then copy | PASS: 7 API + 8 page checks on each | Runtime comparison above |


The core command runs workspace type checking, ESLint, formatting, unit/component,
Node API and schema tests. Django contract coverage explicitly includes queue,
tenant isolation, demo identity, booking/retry, consultation, laboratory, beds,
emergency, hospital settings and payments; Python adds safety and deterministic
queue parity. The original Node-only spy cases are not part of that selected
contract run; their Python equivalents remain in pytest. No wholly green full
1,935-case Node-against-Python result is claimed.

The production browser suite uses built frontends, DEMO_MODE=false, production
security settings and a limited database role, with stand-in/off providers.
Development coverage adds guest booking, live queue, consultation, lab delivery,
emergency, ward operations, offline queue replay and no-show recovery. The built
offline suite uses the original Node API; this is stated separately from Django.
Website checks use the actual bilingual static export, accessibility, responsive
layouts, reduced motion and no-JavaScript rendering.

Long production/development browser runs disable trace recording to limit memory
pressure. Assertions, one-worker execution and zero retries are unchanged; failure
screenshots/videos and logs are retained. Full details of executed commands are
in .local/verify-copy.ps1 and each verify-*.log file.

## Failures and diagnostic findings

### Confirmed clock-skew defect in chamber closure

A separate, disposable-database diagnostic advanced the Django API's test clock
by **1,000 ms** relative to PostgreSQL. Declaring the doctor arrived returned
200; immediately ending the chamber returned **500 INTERNAL**. The error trace
identified `sessions_actual_window_ordered` while persisting the queue projection.
This is a diagnostic reproduction of a defect, not an acceptance-test pass.

The online arrival controller stamps arrivedAt with the API/application clock
(`backend/django/medlive/controllers/queue.py`, declare_arrived). Queue event
serverTs comes from PostgreSQL clock_timestamp()
(`backend/django/medlive/repositories/queue_event.py`). The reducer takes the
former for doctorArrivedAt and the latter for endedAt, and sessions requires
actual_end >= actual_start. A sufficiently ahead API clock can therefore make a
rapid, valid end operation fail that constraint. The same two-clock pattern is
present in the original Node implementation; this controlled reproduction was
performed against Django in the copy, not a live deployment.

The probe uses a test-only clock override; production does not accept that
override from ordinary request headers. It simulates server/database clock skew,
not an unauthenticated public-header exploit. Raw evidence:
[probe outcome](../.local/clock-skew-probe-result.json),
[trace](../.local/clock-skew-probe.log),
[probe source](../.local/clock-skew-probe.test.ts).

The initial 344-case selected Django contract run had three failures around
SESSION_ENDED (500 instead of 200, and the next action consequently not refused).
The complete queue file then passed 35/35 in isolation, without a code change.
The controlled probe establishes a real failure mechanism; it does not prove
that every intermittent failure in the initial run had exactly that cause.

### Ten failures in the full Node/unit/schema run

The core run completed **8,138 passed / 10 failed, 168 passed files / 4 failed
files**. These are **not** the historical ten Node-process-spy incompatibilities
when running the original Node suite against Python: this run tested Node itself.

| Failing file | Cases | Observed failure |
| --- | ---: | --- |
| notificationSender.test.ts | 2 | Retry-state assertions reached the timing check, but remaining waits were 15.033446 s and 60.032048 s, above strict <=15/<=60 bounds |
| standbySelfServe.routes.test.ts | 1 | Ending a chamber with a prepaid person still waiting returned 500 instead of 200, so the refund-eligibility assertion could not complete |
| database/tests/emergency.test.ts | 5 | Timestamped fixtures hit emergency_cases_closed_after_created, including cases intended to test other constraints |
| database/tests/referrals.test.ts | 2 | Timestamped fixtures hit referrals_timeline_in_order or emergency_cases_closed_after_created instead of the intended assertion |

The emergency/referral fixtures construct some timestamps with new Date(), while
database defaults use database time. Retry timing also compares an application
timestamp with database now(). These assertions are sensitive to the relative
clocks and request timing. A later host/database clock sample was approximately
7 ms apart with 14 ms query round-trip time; it is not proof of the offset at
each earlier failure. The constraints were not weakened, tests were not skipped,
and a later passing suite does not erase these red results.

The immediate follow-up is to use a consistent authoritative clock for related
lifecycle timestamps and deterministic fixture/timing tests. Application behavior
or test expectations were not rewritten as part of this verification-only task.

### Intermittent emergency tracking page in development

The eight-spec development workflow selection finished **80 passed / 1 failed**.
The failed emergency-burn case reached the patient's emergency/onway route, but
the onway-status element did not appear within 15 seconds. The retained page
snapshot showed the application header/navigation and an empty main region. This
is not evidence that the complete patient-to-ER flow succeeded in that run.

One deliberate isolated reproduction attempt of the same case then passed,
without a code change or increased timeout. It exercised ranking, the patient's
tracking page and the ER notification. The initial failure remains recorded;
the isolated pass is not a claim that the intermittent navigation problem was
fixed. In combination with the initial original-checkout development-server
stall, this deserves investigation of cold compilation/hydration under local
resource pressure. That explanation is a hypothesis, not a proven root cause.

The full failed run's screenshots, video and error context were preserved under
.local/generated-evidence/development-failures before another suite could replace
test-results. The main runs and isolated attempt all use zero Playwright retries.
Raw logs: [development](../.local/verify-development.log),
[isolated emergency case](../.local/emergency-isolated.log).

## Scope of the conclusion

The checks concern local software behavior on synthetic data. They do not verify
live SMS, real bKash/Nagad credentials, target hospital hardware, a real-patient
deployment or a provider's production service. The full development browser suite
is distinct from the selected workflow run; exact executed counts are recorded
above. Passing an entry page alone is never reported as a completed clinical flow.

## Final running state and handover

The final standalone copy passed the seven API probes and eight page probes
again after the suites finished. All four listeners were inspected by PID and
command line and belong to **V:\STARTUP\medlivebd**, not the original checkout.
The default Django API is healthy and ready, schema 0063. The original checkout's
app processes are stopped; its source and the shared demo database were preserved.

| Service | Address |
| --- | --- |
| Patient app | http://localhost:3000 |
| Staff console | http://localhost:3100 |
| Company website | http://localhost:3200/en or /bn |
| Django API readiness | http://localhost:4000/readyz |

From this copy, stop with `./run.ps1 -Stop`, and restart with
`./run.ps1 -Background -SkipInstall`. The database is still the existing local
PostgreSQL instance; copying the project did not create an independent copy of
its database. Run one checkout at a time on these ports.

Final evidence: [runtime](../.local/copy-final-runtime.json),
[process ownership](../.local/final-process-ownership.json),
[startup log](../.local/final-startup.log).

Tests regenerated 170 production-workspace captures and eight development
captures. Those fresh files were copied under .local/generated-evidence, and
the approved tracked reference images were restored. Failure screenshots/videos
are preserved separately. No application source, database constraint, assertion,
authentication rule or dependency version was changed during this audit. The only
intentional project-document changes are this report and the status handover;
no remote branch, public deployment or real provider was changed.
