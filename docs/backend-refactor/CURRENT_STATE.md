# Current Python backend layout — 28 October 2026

Owner requested Django/Python only and domain folders directly under `backend/`.
The previous `backend/django/medlive/modules/` hierarchy is removed. Django project
configuration is at `backend/core/settings.py`, with ASGI, URLs and ordered route
composition alongside it. Core helpers are grouped into security, database, HTTP,
validation and observability packages. The 17 domain owners sit directly under
`backend/`; queue and platform folders are named `queues` and `platform_admin`
to avoid Python standard-library collisions. See the [backend guide](../../backend/README.md).

The Node server entry point, workers, runtime scripts and deployment option are
retired. Only historical test references remain under `testing/`, with no serving
command. Shared TypeScript rules used by the frontends and SQL migrations remain
outside the backend. SQL schema ownership and existing request/security contracts
are preserved. The old ownership notes below describe the earlier checkpoint.

# Backend baseline

Source baseline: master 0b4d968; the preceding local-copy audit is preserved at
fc7c4d9. This task targets medlivebd, overriding the downloaded briefs' old
HealthCare working-directory example. The original checkout remains the reference.

The active default is Django/DRF + python-socketio under backend/django. The Node
API/workers remain a supported rollback runtime and contract oracle. SQL migrations
own the 63 public RLS tables; Django has no ORM models or migration ownership.
Do not add QuerySet filtering to SQL result dictionaries.

Observed organization: 27 route modules, 26 controllers, 39 services and 29
repositories are spread across global layer directories. core/pipeline.py owns
identity, body bounds, CORS, authorization, scope and response/error translation.
Ordered core/router.py contracts must survive resource-view conversion. Commands,
audit, queue events, outbox and post-commit broadcasts remain service responsibilities.

Observed correctness gap: online doctor arrival uses application time while queue
event timestamps come from PostgreSQL. A controlled +1 second application clock
produced a chamber-end 500. Schema fixtures and retry assertions also mix clocks.
Baseline results and exact failures are in LOCAL_COPY_VERIFICATION_2026-10-28.md.

Optimization targets: colocated domain ownership; SQL-backed DRF read views behind
the existing pipeline; bounded query inputs; scoped SQL-count/time observation;
fixed query growth rather than speculative indexes or a new distributed cache.
Live/clinical/auth responses retain no-store and their authorization boundaries.

## Implemented ownership

All 116 existing business-layer files now live under `backend/`.
The ordered composition remains `core/routes.py`; `test_seam.py` is
still test-only. Core, pure domain rules, adapters and realtime transport retain
shared ownership. No ORM models, new migrations, provider activations or Redis
were introduced. Only real packages were created; no empty app/CRUD stubs.

| Module | Existing responsibilities |
| --- | --- |
| catalog | public search, hospitals, doctors, sessions/availability |
| identity | staff/patient authentication, guest identity, access guards |
| queue | event log/state, sessions, scheduling/materialisation, sync |
| booking | booking, registration, standby and slot offers |
| clinical | visits, prescriptions, records and consent |
| beds | capacity, requests and admissions |
| emergency | public matching, inbound alerts and ER transitions |
| referrals | inter-hospital handovers |
| laboratory | orders, reports and pharmacy dispensing |
| hospital | settings, branding and assigned desks |
| platform | onboarding, agreements/modules, portals, deployment config |
| reporting | hospital administration and national aggregates |
| imports | files, mappings and import application |
| payments | holds, callbacks/webhooks and mock payment |
| messaging | notification outbox, sender and signed links |
| demo | synthetic demonstration setup and identity |
| operations | liveness/readiness, heartbeats and job scheduling |

Within a module, `urls` declares contracts, `views` translates HTTP, `services`
orchestrates transitions/transactions and `repositories` owns SQL. A small layer
uses a file; related resources use a package. Cross-domain workflow transactions
retain the established explicit repository/service calls; moving them across
independent transactions would weaken queue/payment/audit guarantees. Boundary
checks reject HTTP imports from services/repositories and SQL outside repositories.

Four catalog collections use real DRF GenericAPIView dispatch and non-model query
serializers behind a scoped permission bridge. Their canonical domain schemas
preserve coercion, limits, stripping and public errors. Detail/command workflows
retain the existing pipeline APIView adapter and explicit route guards; no extra
HTTP methods or secondary unguarded URL entry points were exposed. The bridge is
not a generic CRUD framework and never applies ORM backends to dictionaries.

The SQL change is a doctor-id predicate plus LIMIT 1 in both runtimes, using the
existing primary key. Existing collection caps, RLS, verification/publication gates,
source timestamps and response representations remain authoritative. No speculative
indexes or private response caches were added. Request-local metrics count application
SQL calls/rows/time and response bytes; connection scope SET operations and background
threads are outside that count. Diagnostics omit raw paths, principal ids and driver
exception values; structured request correlation and stack frames remain.
