# Backend modular monolith: structure, DRF views, filters, and optimization prompt

For the frontend counterpart, use [Frontend architecture, dashboard patterns, caching, and optimization prompt](FRONTEND.md).

Use this document to reorganize an existing backend. It specifies architecture and engineering work; it does not introduce new healthcare features or copy another product's workflows.

**Target:** `V:\STARTUP\HealthCare`. Copy the complete prompt in section 2 into a coding-agent session opened in that repository. The agent should inspect, plan, implement in stages, and verify the authorized backend changes.

## 1. Important compatibility context

A read-only inspection found these structural facts in the target project:

- Django implementation: `backend/django/`, with configuration and application code under `medlive/`.
- Existing organization: `routes/`, `controllers/`, `services/`, `repositories/`, `core/`, `domain/`, `adapters/`, and `realtime/`.
- Django REST Framework is already a dependency, but requests currently enter a custom pipeline and ordered router rather than ordinary resource-specific generic views.
- Database access is primarily explicit SQL through repositories and a scoped database wrapper. SQL migrations under `database/migrations/` own the schema. Hospital/patient/guest database scope and pooled connection handling are deliberate behavior.
- A TypeScript API and workers also exist. The executing agent must establish their current runtime/parity responsibilities before changing or removing anything.

Consequently, **a resource backed by SQL dictionaries cannot acquire correct ORM filtering and pagination just by inheriting `ListCreateAPIView`**. Native DRF generics need a compatible data/query layer. The prompt below handles both ORM-backed resources and existing SQL-backed resources, with a controlled path toward the desired Django app structure.

These notes are a starting point, not a full target-project audit. Recheck the current checkout before implementation. No target application code was changed while writing this prompt.

## 2. Copy-and-run prompt

````text
You are working in V:\STARTUP\HealthCare.

TASK
Reorganize and improve this project's BACKEND as a domain-based modular monolith.
Focus on folder/module responsibilities, Django/DRF views and serializers, validated
filtering, pagination, query efficiency, indexes, caching, and the tests needed to
prove that the refactor preserves behavior.

This is an architecture/refactoring task. Preserve the project's actual healthcare
use cases. Do not introduce features or workflows from a different product. Do not
redesign frontend pages, invent clinical behavior, or replace working business rules.

The desired result is working code with clear module boundaries and measured
improvements. A directory rename alone is not completion. Do not promise perfection
or performance from a folder layout; prove relevant properties with checks/tests.

A. READ AND DISCOVER BEFORE EDITING

1. Read repository instructions, including applicable AGENTS.md/CLAUDE.md and the
   project's current backend, database, product and status documents. Follow their
   authority and working rules. This prompt specifies engineering organization; it
   does not silently override product requirements, dependency approval rules,
   clinical/tenant rules, or deployment policy.
2. Inspect git status and preserve unrelated work. Identify the active Django entry
   point, API routes, worker entry points, tests, and any TypeScript compatibility
   runtime. Do not assume an old implementation is unused merely because Django exists.
3. Trace representative list/detail/create/update/delete and workflow requests end
   to end: routing, parsing, principal/auth, role/module gate, database scope, input
   validation, service, repository, transaction, audit, response, and live events.
4. Identify schema ownership. Inspect existing SQL migrations, constraints, RLS,
   triggers/functions, connection pool, scope setup, money/date conversion, and
   migration tools. Do not read/output database rows or environment secret values.
5. Determine whether each resource uses Django models/QuerySets or raw SQL/repository
   result dictionaries. Record which parts can use native DRF generics immediately
   and which need a compatibility stage. Never invent missing ORM mappings.
6. Establish what is actually messy: oversized modules, cross-domain writes, circular
   imports, duplicated validation, SQL in HTTP handlers, repeated per-row queries,
   inconsistent filters/pagination, unsafe caches and missing regression coverage.
7. Map current API contracts: path/trailing slash, method, auth, input names, response
   envelope, types, dates, error codes, status, pagination and side effects. Preserve
   them unless an intentional contract change is explicitly in scope.

B. PRODUCE AN IMPLEMENTABLE PLAN

Create or update only the architecture documents needed for this task:
  docs/backend-refactor/CURRENT_STATE.md
  docs/backend-refactor/PLAN.md
  docs/backend-refactor/VALIDATION.md

CURRENT_STATE must contain a concise module/route/data-access map and observed gaps.
PLAN must contain ordered vertical slices with:
  current symbol/path -> destination -> callers -> preserved contract -> tests
  schema/migration impact -> rollback -> acceptance condition.
VALIDATION must record commands actually run and results, including baseline failures,
before/after query/payload evidence, and remaining unverified behavior.

For every finding distinguish:
  observed implementation / measured result / proposed improvement.

Then implement the plan in bounded stages under the project's authorization rules.
Do not stop after writing documents if implementation is authorized. Do not interpret
this prompt as permission to deploy, reset databases, replace patient data or release.

C. TARGET ORGANIZATION

Keep the existing backend root and configuration package unless changing them solves
a concrete problem. Organize business behavior by domain rather than leaving every
domain scattered across global routes/controllers/services/repositories directories.

Recommended shape, with <domain> chosen from EXISTING project responsibilities:

backend/django/
  manage.py
  medlive/
    settings.py                    # Preserve working deployment/env contract
    urls.py                        # Root composition and migration route ordering
    asgi.py                        # Existing runtime/socket composition
    core/                          # Shared technical foundations, not business rules
      auth.py                      # Existing identity/session behavior or its adapter
      scope.py                     # Principal -> permitted database/request scope
      db.py                        # Existing scoped SQL connection/transaction boundary
      errors.py                    # Stable public errors and exception translation
      logging.py                   # Structured safe logs and request correlation
      pagination.py                # Agreed pagination helpers/classes
      cache.py                     # Key generation, TTL, invalidation primitives
      performance.py               # Query/time/payload observation when useful
    domain/                        # Existing shared pure types/reducer/rules
    realtime/                      # Shared transport; domain-specific delivery has owners
    modules/
      __init__.py
      <domain>/
        __init__.py
        apps.py                    # Only when registered as a Django app
        urls.py                    # Explicit resource/command routes
        views.py                   # Thin generics and command APIViews
        serializers.py             # Read/write/query-input/command contracts
        permissions.py             # Resource capability/object rules
        filters.py                 # Explicit filtering and ordering contract
        pagination.py              # Only resource-specific overrides
        selectors.py               # Optional read orchestration, not duplicate SQL
        services.py                # Business commands and transaction orchestration
        repositories.py            # Existing SQL data access when retained
        models.py                  # Only real, reviewed ORM model mappings
        integrations.py             # Only a provider owned by this domain
        tasks.py                   # Only if this domain owns background work
        tests/
          test_api.py
          test_permissions.py
          test_filters.py
          test_queries.py
          test_services.py
  tests/                           # Preserve existing suite while migrating ownership
database/migrations/               # Keep current authoritative migration mechanism

This tree specifies responsibilities, not a demand to create empty files. A small
domain may start with urls/views/serializers/services/repositories and extract others
when justified. Use a package instead of a large file when it materially helps.
Keep one canonical implementation of each rule; do not maintain old and new copies.

If an established equivalent layout already works, retain its names and apply these
boundaries. Avoid a gratuitous second configuration package, shared "utils" dumping
ground, universal CRUD engine, or abstract repository layer over every ORM operation.

D. MODULE AND IMPORT RULES

HTTP views -> serializers/permissions -> services for commands
HTTP views -> scoped selector/repository for reads
services -> repositories or explicitly supported ORM access
repositories -> existing scoped DB wrapper
domain rules -> pure project domain code where already established

- Route files declare paths; they do not execute SQL or business decisions.
- Views translate HTTP input/output and choose the correct policy/representation.
- Services own business transitions, audit/events and transaction boundaries.
- Repositories own parameterized SQL when SQL is the established persistence layer.
- Optional selectors compose reads; do not add an extra pass-through layer everywhere.
- A module may call another module's public service/selector when required. It must
  not import another domain's HTTP view or write its private tables opportunistically.
- Shared code must be genuinely shared technical/pure domain behavior. Domain-specific
  logic stays with its owner. Do not fix circular imports with scattered lazy imports.
- Update existing import/layering tests when paths move, preserving their protection.
- Keep compatibility exports only while known callers migrate; record their removal.

E. DRF GENERIC VIEW POLICY

Use standard resource views where their persistence/query contract supports them:

  ListAPIView                  GET collection
  CreateAPIView                POST create
  ListCreateAPIView            GET collection + POST create
  RetrieveAPIView              GET detail
  UpdateAPIView                PUT/PATCH detail, if reads are intentionally absent
  RetrieveUpdateAPIView        GET + PUT/PATCH detail
  RetrieveDestroyAPIView       GET + DELETE detail
  RetrieveUpdateDestroyAPIView GET + PUT/PATCH + DELETE detail
  DestroyAPIView               DELETE detail
  GenericAPIView               shared serializer/query helpers with explicit behavior
  APIView                      custom commands, aggregates, exports and callbacks

Do not expose PUT or DELETE just because a convenient base class provides them.
Constrain methods to existing contracts. Preserve PATCH behavior and existing command
methods. DELETE may mean deactivate/cancel/reverse under current rules; preserve that.

For an ORM-backed collection/detail pair:
- get_queryset(): principal visibility + tenant scope + optimized read shape.
- get_permissions(): action permission, not merely "authenticated".
- get_serializer_class(): explicit list/detail/write representation.
- get_serializer_context(): prepared request-wide policy/calculations.
- filterset_class/search_fields/ordering_fields: allowlisted query behavior.
- pagination_class: stable bounded pagination.
- perform_create/update(): server-owned fields and the established service boundary.
- get_object(): preserve scoped lookup and object permission checks.

For LIST: scope the collection; object permissions are not automatically evaluated
for every row. For CREATE: explicitly authorize ownership/related IDs because there
is no existing object on which to run an object permission. For UPDATE: validate all
replacement related IDs, not only permission on the original record.

For SQL-backed resources:
- Start with thin APIViews/GenericAPIView using validated serializers and the existing
  services/repositories. Implement bounded filtering/pagination inside repositories.
- Do not hand dictionaries/lists to ORM filter backends and assume QuerySet semantics.
- Do not fetch all rows into Python to imitate generic list filtering/pagination.
- If moving a resource to native generics is justified, define the exact QuerySet and
  model mapping plus auth/scope/transaction/error compatibility first, then migrate
  one resource with parity tests. Unmanaged model mappings, if chosen, must accurately
  reflect existing schema and do not transfer migration ownership automatically.
- Do not create a second CRUD framework just to make raw SQL inherit a generic name.

Use explicit per-module URLs. Mount converted routes before a retained catch-all
only when ordered-route parity proves there is no shadowing or ambiguous dispatch.
Preserve the existing no-slash/slash behavior instead of enabling redirects globally.

F. PRESERVE THE SECURITY PIPELINE WHILE INTRODUCING VIEWS

The existing API has its own principal, scoped SQL access and request pipeline.
New views must retain equivalents of every current guard, in the necessary order:
request identity -> parsing/size bounds -> auth/principal -> hospital/patient/guest
scope -> role/module/consent policy -> validation -> service/repository -> safe reply.

- Adapt existing authentication deliberately. Do not make a custom principal look
  like Django's default User by assumption or replace tokens/sessions casually.
- Do not mount a new view outside the established protections with empty DRF defaults.
- Maintain existing error envelopes, redaction, request IDs, CORS and rate limits.
- Set/reset effective database scope on the actual pooled connection used by the
  query. Python-level filtering does not replace database-level isolation.
- Direct ORM access can bypass the scoped SQL wrapper. Prove its scope establishment
  and cleanup, including rollback and connection reuse, before enabling it.
- Preserve record/role/module/consent checks and access audits. Public availability
  aggregates and identifiable records need different data contracts.
- Log technical diagnostics without patient identifiers, query values, clinical data,
  credentials, tokens, OTPs or provider payloads.
- Keep the project's demo/test-data restrictions and its existing integer money and
  serialized date/ID conventions. Do not replace them with unrelated project defaults.

G. SERIALIZER RESPONSIBILITIES

- Use serializers.Serializer for non-model inputs, repository response contracts,
  filter parameters and command bodies. Use ModelSerializer only with real ORM models.
- Explicitly allow fields; protect owner/scope/audit/calculated/private fields.
- Separate list/detail/write/compact/public/admin serializers only when contracts differ.
- Normalize and validate query/body types, date ranges, limits, enums and related IDs.
- PATCH must validate the resulting state using unchanged existing fields as needed;
  omitted data is not the same as explicitly empty/null data.
- Service invariants must still hold for workers and non-HTTP callers. Do not relocate
  all business validation into serializers and leave other entry points unprotected.
- SerializerMethodField and properties must consume prepared rows/relations/context;
  no hidden database lookup/provider call per output row.
- If write responses require a read representation, explicitly serialize the saved
  result after the service succeeds. Keep field casing and scalar types compatible.
- Do not run status transitions or background work from representation methods.

H. FILTERING, SEARCH, ORDERING AND PAGINATION

For each list endpoint define an explicit query-input contract:
  supported names/types; enum values; equality/multi-value/range semantics;
  date/timezone rules; search length/fields; ordering allowlist/tie-break;
  default/max page size; envelope; unknown-parameter/error behavior.

Store resource-specific logic in modules/<domain>/filters.py. Shared primitives may
live in core. Scope is derived from the actor first; user filters can only narrow it.

ORM path:
- Use django-filter FilterSet where already installed/approved and appropriate.
- Use suitable typed filters for bool/date/time/ranges/multi-value values.
- Use DRF SearchFilter/OrderingFilter with explicit fields and controlled cost.
- Match serializer/relation loading to the filtered, ordered, paginated query.

SQL path:
- Validate query parameters with a query serializer or existing validated schema.
- Translate supported filters into parameterized repository predicates.
- Resolve ORDER BY from a fixed public-name -> trusted SQL-expression map; never
  interpolate a client-provided SQL identifier, direction, or expression.
- Apply hospital/owner/RLS restrictions before counts, limits and offset/cursors.
- Keep count and rows aligned to identical predicates without join duplication.
- Use bound limit/offset values and deterministic sorting with a unique tie-break.

Both paths:
- Reject invalid or inverted ranges and unsafe/expensive ordering.
- Define exact inclusive/exclusive date boundaries and preserve current semantics.
- Keep stable results for equal sort values. Review page-number cost on large lists;
  use cursor/keyset pagination for suitable high-volume append-only feeds if the
  contract supports it. Do not silently replace response envelopes.
- Cap page size, search length and multi-value list sizes. Large exports are separate
  endpoints/jobs, not an unlimited page_size escape hatch.
- Preserve existing unknown-parameter behavior unless changing it intentionally.
- Add filter tests for combined predicates, empty results, invalid inputs, duplicate
  join rows, ordering ties, maximum sizes, and foreign-hospital attempts.

I. N+1 AND DATABASE QUERY OPTIMIZATION

Measure representative cold reads before optimizing. Trace every nested field,
computed property, relation and helper invoked for a page.

ORM-backed reads:
- select_related for needed FK/one-to-one data; avoid unrelated wide joins.
- prefetch_related/filtered Prefetch for plural paths; consume the prepared collection
  without issuing a different relation query per row.
- annotate/Exists/Subquery/filtered aggregates for counts, flags and latest values.
- Protect aggregates from join fan-out; use distinct only where semantically correct.
- Use only/defer/values thoughtfully; deferred-field access can reintroduce N+1.

SQL-backed reads:
- Replace one query per returned row with appropriate joins, grouped aggregates,
  EXISTS, window functions, lateral/subqueries or bounded batched IN/ANY reads.
- Parameterize values; keep scope explicit and preserve existing RLS.
- Select needed columns. Detail relations/documents do not belong in every list row.
- Fetch parent pages before batching large child collections where appropriate; avoid
  a join that duplicates parents and breaks pagination or count semantics.

Across both:
- Separate list/detail/compact read shapes. Return narrow options and server-side
  summaries instead of downloading whole collections to compute UI counts.
- Compute shared policy/reference data once per request. Avoid repeated price/rule/
  permission lookups across serializer fields when the result can be prepared once.
- Use bounded batches for imports/exports; stream where practical. Bulk APIs may
  bypass save hooks/signals: preserve audit, event and business side effects explicitly.
- Inspect query duration and plans, not query count alone. One giant query can be
  worse than several bounded queries.
- Add small-versus-larger dataset growth tests and realistic page budgets, including
  authentication/scope overhead. Distinguish application SQL from pooled scope setup.

J. INDEX AND CONSTRAINT PLAN

Keep schema changes in the project's authoritative migration system.

For each proposed index record:
  endpoint/query -> predicates/order -> existing indexes -> proposed columns/order
  -> representative plan evidence -> write/storage impact -> migration/rollback.

- Inspect primary/unique/FK indexes and existing SQL definitions first.
- Match composite indexes to real hospital/owner equality filters and useful
  status/date/order access paths; column order depends on measured predicates.
- Use partial indexes only where predicates/selectivity justify them. Choose
  full-text/trigram support only for a demonstrated search need and allowed dependencies.
- Preserve unique/check/FK constraints, RLS policies, triggers and stored functions.
- Treat uniqueness/nonnegative/state invariants as correctness constraints, not just
  application validation. Consider races, existing duplicates and backfill order.
- Do not add every possible index or remove an index from one endpoint's plan alone.
- Review lock time on large tables and concurrent-index migration options.
- Validate PostgreSQL plans with representative synthetic data. EXPLAIN ANALYZE runs
  the statement; use a safe environment and do not execute dangerous writes to inspect.

K. CACHING THAT MATCHES PRIVACY AND FRESHNESS

Optimize expensive cold queries before caching them. Cache selected read models only
when staleness and privacy allow it; do not add Redis merely because another project
used it. Follow this repository's dependency/infra authorization rules.

Every proposed cache must have an owner and a policy:
  payload -> scope/key dimensions -> TTL/allowed age -> invalidating writes/events
  -> outage behavior -> sensitive-data policy -> tests.

- Authenticate/authorize and resolve effective scope before private cache lookup.
- Keys must include all result-changing dimensions: effective hospital/owner, role/
  permission/consent version when applicable, locale, filters, sort, page and schema.
- Use canonical bounded keys/digests. A user ID plus query string may be insufficient
  after membership/consent changes. Never log keys containing private values.
- Separate genuinely public operational data from personal/clinical responses. Honor
  existing no-store restrictions and age/freshness fields. Never turn stale capacity
  into an authoritative current figure or cache authorization indefinitely.
- Invalidate after committed writes through every API, task, import and admin path.
- Define TTL/jitter and bounded cold-build coordination for expensive hot keys.
- Cache outage should not create an uncontrolled database stampede. Security locks/
  throttles and public read caches need different failure policies.
- Process-local memory is not a shared fleet cache. Aliases/logical Redis databases
  are not physical capacity isolation or a durable idempotency guarantee.
- Keep cache, HTTP proxy caching, broker state and authoritative database data distinct.
- Test miss/hit/expiry, mutation invalidation, role/scope/consent change, outage, and
  cross-hospital/cross-user leakage with synthetic data.

L. KEEP COMMANDS, TRANSACTIONS AND REALTIME CORRECT

- Preserve existing services and state machines. A workflow command is not arbitrary
  model PATCH merely because a generic update view is available.
- Keep state-changing transactions short; use the established scoped transaction
  helper and row/advisory locking where the existing invariant requires it.
- Set a consistent lock order. Test contention and rollback against PostgreSQL.
- Preserve durable idempotency keys and payload matching; duplicate requests must not
  duplicate writes, events, notifications, queue advancement or provider operations.
- Schedule cache invalidation/event delivery after committed changes using the existing
  reliable mechanism. on_commit does not alone provide durable event delivery; retain
  an existing outbox/event log and don't replace it with an in-memory callback.
- Preserve the single source of domain/reducer truth. Never recreate queue/event rules
  in a serializer, SQL fragment or generic view during the structural refactor.
- Preserve live-event ordering/versioning, reconnect/replay, room authorization and
  freshness behavior. Keep Socket.IO compatibility if that is the existing transport;
  do not replace it with Channels just to match a different repository.
- Retain the current worker runtime unless migrating it is explicitly necessary.

M. SETTINGS, CONNECTIONS AND OPERATIONAL COST

- Reuse current validated environment configuration. No hard-coded credentials or
  sample secret values. Do not enable unused Django auth/admin/session infrastructure.
- Preserve bounded psycopg pooling and the current ASGI/thread/connection lifecycle
  until alternative behavior is measured. Do not copy a different app's connection
  settings or remove per-request cleanup merely because Django defaults differ.
- Budget connections across processes, replicas, rollouts, workers and operational
  reserve. A per-process pool maximum is not a fleet-wide maximum.
- Keep bounded body/file sizes, query/provider timeouts and rate-limit behavior.
- Record request correlation, normalized route/status, duration, safe SQL count/time,
  cache observation and response size. Redact values and SQL parameters.
- Preserve liveness/readiness semantics and structured public errors. Do not add a
  production monitoring stack or deployment changes outside this task's scope.

N. EXECUTION ORDER AND GATES

Stage 0 — Baseline and plan
  Read instructions; establish active runtimes/contracts; map current modules and
  data ownership; run relevant existing checks; document current failures.
  Done: a source-backed plan with explicit boundaries, risks and validation commands.

Stage 1 — One domain moved cleanly
  Pick a low-risk existing resource; collocate its routes/contracts/service/repository;
  update callers/import rules; retain stable routing and behavior.
  Done: no duplicate implementation; focused contract/layering tests pass.

Stage 2 — HTTP and validation cleanup
  Introduce thin resource views and serializer/query contracts. Use native generics
  only with a proven compatible scoped QuerySet; keep SQL-backed workflows intact.
  Done: auth/scope/error/type/route parity, including failure cases, passes.

Stage 3 — Filters and pagination
  Add one documented bounded filtering/ordering contract to the selected resource;
  preserve existing clients and envelopes; reuse shared pagination primitives.
  Done: filter, ordering, page-bound and tenant-isolation coverage passes.

Stage 4 — Queries and indexes
  Measure cold queries; remove N+1/overfetch; inspect plans; introduce only justified
  migrations through the existing schema tool.
  Done: behavior parity and measured query/payload evidence; migration risks recorded.

Stage 5 — Optional caching
  Cache only justified reads with scope/freshness policy and complete invalidation.
  Done: hit/miss/invalidation/outage/privacy tests pass; cold path remains bounded.

Stage 6 — Remaining domains
  Apply the proven pattern one vertical slice at a time; migrate references and delete
  obsolete wrappers only after proving they have no callers. Keep one owner per rule.
  Done: complete scoped migration map with no broken imports or accidental new APIs.

Stage 7 — Regression and handover
  Run the project's required backend tests/parity/layering checks and relevant browser
  contract/canary tests when backend behavior they depend on is touched. Do not edit
  frontend UI as part of this task. Summarize remaining optional improvements honestly.
  Done: final validation record, clear module map and rollback/deployment notes.

Narrow stages to obey existing branch/file-count rules. Do not merge or push red
changes, rewrite migration history or deploy implicitly. An architectural decision
that would replace schema ownership/auth/runtime must be called out, not hidden
inside an apparently cosmetic folder move.

O. VALIDATION AND DEFINITION OF DONE

Discover and run the project's actual commands. This repository has pytest Django
configuration and cross-runtime/parity tests; do not assume manage.py test alone
collects all pytest tests. Use its test settings and authorized synthetic database.

Use checks appropriate to changes, such as:
- Django system checks under the appropriate environment.
- Affected pytest unit/API/repository/filter/query/layering suites.
- Existing TypeScript-to-Django API/domain parity tests where routes/rules change.
- Existing SQL migration verification when schema changes; do not create a second
  makemigrations workflow unless schema ownership is intentionally changed.
- PostgreSQL hospital/owner isolation, pool reuse/rollback, contention and duplicate
  request cases, using the restricted application role as well as required admin setup.
- Existing realtime canary/replay and dependent journey checks when those paths change.

For every migrated feature require:
  [ ] One domain owner and coherent placement of all responsibilities.
  [ ] Explicit routes/methods and safe read/write/query serializers.
  [ ] Correct collection, object, create and related-ID permissions.
  [ ] Existing auth/module/consent/RLS and safe response fields preserved.
  [ ] Bounded validated filters/search/order/pagination.
  [ ] No per-row query growth; cold path budget and payload measured.
  [ ] Index/migration rationale documented where applicable.
  [ ] Cache freshness/key/invalidation/outage rules verified if caching exists.
  [ ] Transaction/audit/event/idempotency behavior preserved.
  [ ] Existing API types/envelopes/errors and live contracts preserved.
  [ ] Focused checks pass; new failures fixed; baseline failures reported separately.
  [ ] No production data, credentials, deployment or unrelated code modified.

Final report: what moved and why; which generic/filter/query patterns now apply;
API/schema compatibility; checks actually run; measured before/after values; remaining
limitations. Do not call an index used, an endpoint fast, or a project fully safe
without the relevant evidence.
````

## 3. Framework references

These references explain framework behavior. The module layout and migration stages above are architectural recommendations to adapt to the target's existing contracts, not requirements imposed by Django.

- [DRF generic views](https://www.django-rest-framework.org/api-guide/generic-views/): resource view classes, hooks and queryset behavior.
- [DRF permissions](https://www.django-rest-framework.org/api-guide/permissions/): collection visibility, object checks and creation boundaries.
- [DRF pagination](https://www.django-rest-framework.org/api-guide/pagination/): pagination configuration and supported strategies.
- [Django database optimization](https://docs.djangoproject.com/en/5.2/topics/db/optimization/): profiling and database access tradeoffs.
- [Django QuerySet reference](https://docs.djangoproject.com/en/5.2/ref/models/querysets/): relation loading, query execution and row-lock details.
- [Django transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/): atomic work and commit callbacks.
- [Django caching](https://docs.djangoproject.com/en/5.2/topics/cache/): backend configuration and cache semantics.

This file is a reusable implementation prompt. Writing it did not perform the refactor or establish runtime performance results.
