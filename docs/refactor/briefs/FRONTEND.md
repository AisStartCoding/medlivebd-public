# Frontend architecture, dashboard patterns, caching, and optimization prompt

**Target:** `V:\STARTUP\HealthCare`. This is a standalone frontend counterpart to the [backend refactoring prompt](BACKEND.md). Copy the complete block in section 2 into an agent session opened in the healthcare repository.

The goal is to improve structure, caching, dashboard consistency and measured performance while preserving the project's own healthcare workflows and approved design. It is not a request to transplant another product's screens or create new clinical behavior.

The expanded prompt explicitly covers **CSR, SSR, SSG/ISR eligibility, React Server Components, streaming, hydration, cache-first/network-first/stale-while-revalidate policies, background jobs, stable-focus dialogs, searchable controls, media lifecycle, safe navigation and reusable browser regression checks**. See the [source-backed reusable-pattern review](FRONTEND_REUSABLE_PATTERNS_REVIEW.md) for evidence and adoption cautions; it is optional reference material, not a dependency of the copyable prompt.

## 1. Context checked before writing this prompt

Read-only inspection covered the reference frontend's query provider/keys, shared dashboard hooks, scope handling, invalidation helpers, dashboard shell/navigation, API client, images and lazy-loading patterns. The useful architectural patterns are reusable; their original business names and visual branding are not requirements for the target.

The healthcare repository already has:

- Separate `frontend/console`, `frontend/patient` and `frontend/site` apps, with Next.js 16.3.8 in the inspected manifests. Preserve app boundaries and check installed framework documentation.
- Shared `@platform/client`, `@platform/ui`, `@platform/domain` and `@platform/i18n` packages. The console/patient/shared-client manifests inspected do not declare TanStack Query; do not assume it is installed or replace their state layer without evaluating it.
- Shared console presentation through `ConsoleWorkspaceFrame`, `ConsoleRail` and `shared/ui/src/console/ConsoleFoundation.jsx`, with approved scoped tokens and Bangla/English controls. Existing design documents distinguish console and patient visual systems.
- An API envelope/error contract, single-flight staff refresh, custom resource hooks and Socket.IO channels. Preserve these rather than adding competing implementations.
- Dexie-backed owner-scoped offline outboxes and timestamped snapshots. These are durable workflow state, not disposable query-cache entries.
- Console/patient service workers that exclude API/socket requests but broadly cache other successful same-origin GET responses. Cache eligibility, portal identity, offline document fallback and update behavior require targeted review before treating this as a safe universal policy.
- Request-specific CSP nonces and `force-dynamic` layouts in the console/patient apps. Removing dynamic rendering to obtain a faster static build could break the security/rendering contract.
- Dashboard code that already retains prior data on refresh failures, displays freshness and guards against older request results. Improve these patterns coherently instead of duplicating them.

These are source observations, not passing performance/security test results. Recheck the current checkout before implementation. No healthcare application code was changed to produce this document.

## 2. Copy-and-run prompt

````text
You are working in V:\STARTUP\HealthCare.

TASK
Audit, organize and optimize the existing FRONTEND, focusing on:
  folder ownership and reusable design patterns;
  dashboard shell/navigation/page composition;
  server-state caching and request coordination;
  query identity, invalidation, cancellation and lifecycle;
  tables, search, filters, forms, charts, lists and secondary panels;
  server/client rendering, loading, code splitting, images/fonts and render cost;
  offline stores, service-worker caching, realtime reconciliation and freshness;
  permissions, hospital/account isolation, accessibility and verification.

Preserve existing healthcare use cases, authorized workflows, APIs, translations,
visual foundations and domain rules. Do not copy marketplace workflows or introduce
new clinical behavior. This is frontend architecture/performance work, not a backend
rewrite, a new design theme, a dependency installation request or deployment approval.

A. DISCOVER THE CURRENT IMPLEMENTATION

1. Read applicable repository instructions, docs/FRONTEND.md, APP_FLOW/product rules,
   current design-foundation notes and status. Follow their authority, dependency
   approval, branch, test and scope rules. Newer approved design decisions may refine
   older styling notes; do not mix unrelated visual systems arbitrarily.
2. Check git status and preserve unrelated work. Identify active frontend apps, shared
   packages, entry points, runtime modes, build tooling and unit/browser tests.
3. Inspect package manifests and installed Next/React documentation. Determine actual
   query/state libraries, compiler settings, server/client boundaries, cacheComponents
   configuration, webpack/workspace resolution and CSP requirements. Do not assume
   framework caching defaults from another Next.js version.
4. Trace key dashboards and customer/patient routes from initial navigation through
   session/scope resolution, data loading, mutations, realtime, offline use and logout.
5. Inventory every storage/cache layer: component state, shared memory, query manager,
   session/local storage, IndexedDB, offline outboxes, Cache Storage/service worker,
   Next server data/route/client-router cache, browser HTTP and CDN/proxy cache.
6. Record all request triggers: mount, route/filter change, role/scope/language change,
   focus, reconnect, timers, socket events, manual refresh, mutation and sibling widgets.
   Find duplicated shell/branding/options/summary requests and unnecessary waterfalls.
7. Map actual problems: giant components, duplicate layouts, inconsistent loading/error
   handling, stale-response races, query-key collisions, broad invalidation, polling
   storms, leaking context/theme, expensive lists/charts and unsafe persistence.
8. Inspect the existing security/offline/reducer design before changing state ownership.
   Never send real patient information to external tools or put private response data,
   tokens or identifiers in screenshots, HARs, logs or performance reports.

B. PLAN AND DELIVERABLES

Create or update:
  docs/frontend-refactor/CURRENT_STATE.md
  docs/frontend-refactor/PLAN.md
  docs/frontend-refactor/CACHE_POLICY.md
  docs/frontend-refactor/RENDERING_AND_CACHE_MAP.md
  docs/frontend-refactor/VALIDATION.md

CURRENT_STATE: source-linked app/package/component/state/request/cache map and real
gaps. Distinguish observed implementation, measured results and recommendations.

PLAN: ordered vertical slices with old path/symbol -> new owner -> callers -> preserved
behavior -> checks -> before/after evidence -> rollback. Separate visual-only changes
from data lifecycle changes so reviewers can understand risk.

CACHE_POLICY: one row per resource/cache with scope, owner, key, source timestamp,
freshness, retention, triggers, invalidating events, persistence and cleanup behavior.

RENDERING_AND_CACHE_MAP: one row per route/major feature with initial-render mode,
server/client boundaries, critical data, browser-only dependencies, hydration source,
cache layers, invalidation, CSP/auth constraints and the reason for each choice.

VALIDATION: commands actually run, results, existing failures, representative mobile/
desktop observations, request counts, transfer/bundle/render evidence and limitations.

Implement authorized slices after preparing a concrete plan; do not stop at advice
if code changes are authorized. Never interpret this task as permission to reset data,
install unapproved dependencies, publish, change remote branches or deploy.

C. TARGET FOLDER AND PACKAGE OWNERSHIP

Preserve the current monorepo and its separate apps. Use existing equivalent names
where they work; these are responsibility boundaries, not mandatory empty files:

frontend/
  console/src/
    app/                          # Routes/layouts/entry composition, not business engines
    components/
      layout/                     # Existing shell/rail/header adapters if extraction helps
    features/
      <existing-domain>/
        components/               # Domain panels, forms, tables, drawers
        hooks/                    # Resource lifecycle and view-state composition
        api.js                    # Thin domain API adapter over @platform/client
        queries.js                # Optional shared query definitions/key factories
        mutations.js              # Command + coherent invalidation rules
        adapters.js               # API data -> explicit display/view model
        filters.js                # UI filter state, query serialization, reset rules
        tests/
    hooks/                        # Only app-wide shared hooks
    lib/                          # Runtime integration; avoid a business-logic dumping ground
  patient/src/                    # Same ownership principles; own app/visual behavior
  site/src/                       # Public marketing; separate caching/design policy
shared/
  client/src/
    api/                          # HTTP envelope, errors, auth integration, cancellation
    realtime/                     # Existing shared Socket.IO transport/reconnect/replay
    offline/                      # Existing stores, snapshots, outbox and sync contracts
    query/                        # Only if justified: common key/lifecycle primitives
  ui/src/
    tokens/                       # Approved semantic spacing/color/type/status tokens
    components/                   # Accessible primitives
    console/                      # Existing shared console foundation/presentation
  domain/                         # Existing pure rules/reducer: one implementation
  i18n/                           # Existing messages, locale, date/number formatting

- Keep route components thin: resolve context and compose features.
- Keep stateful feature hooks separate from reusable presentational components.
- Do not move every existing file just to produce this tree. Start with the slice
  being improved; preserve stable exports while callers migrate.
- No domain feature imports another feature's route/page or private component state.
- Shared packages must not depend on an app. Avoid a barrel export that pulls large
  client-only/offline/chart code into server or marketing bundles unnecessarily.
- Preserve current file extensions, module resolution and lint boundaries. Do not
  convert the whole repo to a different language or bundler as a side effect.

D. DEFINE STATE OWNERSHIP BEFORE CACHING

Assign one owner to each kind of state:
  authoritative business data -> backend;
  remote resource/read model -> established query/resource layer;
  live event/replay state -> existing realtime/domain controller;
  unsent durable actions -> existing owner-scoped offline outbox;
  unsaved form input -> feature form state;
  shareable non-sensitive filters/tab/page -> route/URL state where compatible;
  temporary disclosure/focus/selection -> nearest useful component;
  session/principal/active hospital -> existing auth/scope owner;
  permitted theme/locale/preferences -> existing shared owners.

Do not copy query results into several contexts/useState values unless there is a
clear purpose such as a deliberate editable draft. Do not make a query cache a second
queue reducer or a duplicate of the durable outbox. React memoization is not a data
freshness, persistence or authorization strategy.

E. SHARED RESOURCE LAYER AND CACHING

Use the established query/resource system consistently. If a new library is genuinely
needed, explain the concrete gap and follow repository approval rules. Do not install
TanStack Query merely to resemble a reference project or build a homemade equivalent
of a full query library. Existing hooks/stores may remain where appropriate.

Where TanStack Query is already installed or approved:
- Own a stable client for the appropriate browser/app session, not on every render.
- Use request-isolated server clients/caches where SSR handles private user data;
  never use a process-global private query cache shared between requests.
- Set per-resource stale/refetch/retention/retry policies; don't rely on defaults.
- Deduplicate related consumers with identical resource definitions and query keys.

Apply the following principles regardless of library:
- Resource identity includes every result-changing dimension: app/resource, effective
  hospital/portal, account/principal identity or safe partition, role/access/consent
  version when relevant, locale, resource ID, validated filters/order/page and schema.
- Avoid putting raw tokens, patient search terms, contact information or clinical
  content in inspectable key strings/telemetry. Use minimal safe identifiers; a digest
  is not permission to persist sensitive data.
- Reuse key factories/resource definitions instead of inventing keys in each widget.
- Cache staleness and inactive retention are different policies. Retaining data in
  memory does not establish that it is still authorized or medically/currently valid.
- Infinite freshness requires a tested update/revocation lifecycle; avoid it for
  permissions or mutable live data without such guarantees.
- Do not keep another hospital/account's result as a loading placeholder.
- A scope switch must immediately change visible identity/data ownership, cancel or
  detach prior reads/subscriptions and ignore results from the previous generation.
- Deduplicate header/rail/page branding, identity, notifications, reference/options
  and summary resources through one owner; do not block primary work on optional data.
- When active consumers need the same resource, share their in-flight read rather than
  issuing one request from every child. Different filters/authorization must not share.

Use this policy classification, with values set from product requirements/baselines:
  immutable build assets -> versioned long-lived asset caching;
  non-sensitive reference options/branding -> bounded reuse, explicit change refresh;
  operational summaries -> approved short refresh interval plus source-age display;
  live state -> authoritative event/snapshot controller with gap recovery;
  personal/clinical detail -> narrowly scoped memory and persistence only as authorized;
  form drafts/outbox -> separate domain-approved lifetime and ownership rules.

Do not copy numerical stale times from another app as universal safe settings.

F. CACHE INVALIDATION AND IDENTITY CHANGES

- Define an invalidation map for every command: affected detail, lists, counts,
  options, summaries and any offline snapshot. Put it in the feature's mutation owner.
- Update precise entries from an authoritative response when supported; invalidate
  remaining affected reads deliberately. Do not refresh the entire app after every edit.
- Cancel/guard an older in-flight read before it can overwrite mutation results.
- For simultaneous mutations, use entity/version-aware reconciliation; rolling back
  one action must not undo a later successful action or incoming realtime event.
- Optimistic behavior needs explicit acceptance/rejection/network-failure states.
  Preserve this product's durable offline actions; do not treat them like disposable
  query mutations with a universal "rollback on network error" handler.
- Default to no blind mutation retry. Retrying writes requires stable idempotency
  and existing domain semantics, including unknown server outcomes.
- On logout/revocation/account/hospital changes, remove or partition private reads,
  detach listeners/sockets, reset route/drawer selection and prevent previous responses
  from repopulating visible state. Cover same-tab and cross-tab session changes.
- Do not delete pending offline actions to clear a read cache. Preserve/quarantine
  them according to existing owner/retention policy; never send them as the next user.
- Scope browser persistence by identity and schema where required. Handle quota,
  corruption, expiry and unavailable storage honestly.

G. REQUEST CLIENT, RETRIES AND CANCELLATION

- Extend @platform/client and existing auth integration instead of scattering raw
  fetch implementations across components. Keep envelope/error/status compatibility.
- Add optional cancellation/timeout support through the whole call chain when needed,
  preserving signatures for old callers. Abort must reach the real network transport.
- Combine caller cancellation with an endpoint-appropriate finite deadline where
  supported; do not silently discard one or leave abort listeners/timers attached.
- Distinguish intentional cancellation, transport failure, invalid response, denied
  permission, expired session, conflict and server failure in UI handling.
- Preserve a useful screen/draft during transient failures. A cancelled obsolete read
  should not show a generic failure toast or sign the user out.
- Reads may retry bounded transient failures with backoff/jitter and Retry-After.
  Avoid retrying deterministic validation/authorization errors.
- Keep one refresh operation in flight under the established session mechanism.
  Audit cross-tab rotation races without changing cookie/token contracts casually.
- Bound request/upload/export fan-out and cleanup; a gallery/table should not create
  hundreds of parallel requests. Don't add one detail request per displayed row.
- Distinguish preventing a late render from cancelling network work: a stale-result
  flag is useful, but it doesn't reduce transport or backend load by itself.

H. NEXT.JS SERVER/CLIENT AND CACHE BOUNDARIES

Make the rendering strategy explicit per route instead of calling everything SSR:
- CSR: browser-driven interactive views and data updates where appropriate.
- SSR/dynamic rendering: request-specific initial HTML; preserve principal/CSP context.
- SSG: prebuilt public content only when request-specific identity is unnecessary.
- ISR/time-based revalidation: eligible public content with an approved staleness budget.
- RSC: server component ownership/data loading; this is not a synonym for SSR or an
  instruction to ship every imported dependency to the browser.
- Streaming/Suspense: let independent sections become available without one slow
  secondary resource blocking the initial shell or primary work.
- Hydration: attach client behavior to initial HTML/data without duplicate reads or
  server/client differences in locale, time, theme, IDs and rendered content.
- Partial prerendering/Cache Components: evaluate only if the installed configuration,
  security model and measured need support it. This is not a mandatory migration.

Client Components can participate in initial server-rendered HTML; 'use client' is
a module boundary, not proof that a component renders exclusively in the browser.
Use browser-only dynamic imports only for dependencies that actually require them.
Do not silence a hydration bug with broad suppressHydrationWarning or disabling SSR.

- Consult installed docs and current cacheComponents/segment settings first. Do not
  conflate server fetch caching, full-page rendering, client router reuse and browser
  query data. Each has a separate lifetime and invalidation mechanism.
- Keep static layout/presentation on the server where appropriate. Place 'use client'
  around interactive entry points and avoid dragging every route dependency into them.
- Never move private session data into a publicly shared fetch/page cache to improve TTFB.
- Do not serialize secrets or unnecessary patient data into server HTML/client props.
- Current patient/console layouts use per-request CSP nonces and dynamic rendering.
  Preserve that security contract; do not force static rendering, ISR or reusable
  nonce-bearing HTML without a deliberate compatible architecture and tests.
- Initial snapshots must carry their source time/version and correct scope. Avoid an
  immediate redundant client fetch if the snapshot meets its resource freshness policy.
- Do not label data freshly updated at hydration when the server snapshot is old.
- Fetch independent data in parallel with bounded fan-out. Keep necessary dependencies
  explicit instead of manufacturing waterfalls through component mount order.
- Use route loading/Suspense/error boundaries where appropriate, and widget-level
  boundaries so one optional report doesn't blank the whole workspace.
- Tune route prefetch selectively. Huge dynamic/private routes may cause unnecessary
  reads, but globally disabling navigation prefetch is not a universal optimization.
- router.refresh(), query invalidation and service-worker cache updates are different
  operations; don't use full navigation/reload as the default mutation strategy.

H1. EXPLICIT CACHE METHODS AND WHERE THEY APPLY

Document selection among these methods; do not enable all of them for every resource:
  request deduplication/memoization -> eliminate repeated equivalent work in the
    supported render/request boundary; not durable storage or cross-user sharing;
  cache-aside -> read scoped cache, fetch on miss, store under an explicit TTL;
  network-first -> ask authoritative source, allow an eligible aged fallback on failure;
  cache-first -> reuse eligible versioned assets, refresh only under its update policy;
  stale-while-revalidate -> show eligible known-old data while updating it, with age
    disclosure and a defined limit; inappropriate where stale authorization/data is unsafe;
  TTL/expiry -> a maximum reuse/retention policy, not an exact live-update scheduler;
  event/mutation invalidation -> invalidate/replace precise committed dependencies;
  conditional HTTP validation -> ETag/Last-Modified/304 only if the real server supports
    it and response variation/privacy are correct; do not invent backend support;
  no-store/no persistence -> an explicit exclusion for data that must not be retained.

For Next server data, choose only APIs supported by the installed cache model:
- fetch cache options such as cache: 'no-store' or eligible cache: 'force-cache';
  explicit next.revalidate/tags when applicable; route segment settings may override
  assumptions about individual requests, especially beneath force-dynamic layouts.
- If Cache Components are enabled, understand 'use cache', cacheLife and cacheTag
  in that model before using them. Do not casually enable the flag or apply shared
  caching to authenticated clinical reads.
- revalidatePath affects route/layout revalidation; revalidateTag handles tagged
  server data. Choose documented stale-while-revalidate versus immediate-expiry
  behavior deliberately rather than copying deprecated invocation signatures.
- updateTag is for supported server-action read-your-own-writes workflows, not a
  client-side substitute for resource-cache invalidation. Preserve the existing API
  architecture; introducing Server Actions solely to call an API is not required.

For browser resource data, reuse/invalidate the established query/store entries.
For HTTP/CDN content, use the actual server/proxy caching contract and Vary dimensions.
For service workers, enforce Cache Storage eligibility yourself. IndexedDB/outboxes
have a separate ownership/retention/replay contract. Image derivative caches have
their own source-URL/version policy. Invalidating one layer does not clear the others.

I. SERVICE WORKER AND OFFLINE CACHE REVIEW

Treat service-worker shell caching, IndexedDB snapshots and durable outboxes as three
different systems. Preserve existing module-specific offline behavior.

Audit both console and patient workers, their registration/warmup messages and every
potential cached GET response. An API-path exclusion alone isn't an allowlist.

- Define exact asset/document eligibility: origin, path, method, content type, status,
  auth/scope properties, cache-control intent, portal parameters and build identity.
- Never cache authenticated API, socket transport, clinical files, tokens/guest-link
  content, private server-rendered documents or permission-dependent responses through
  a generic successful-GET rule.
- Cache Storage does not automatically enforce HTTP no-store directives. Implement
  the approved eligibility policy explicitly; headers alone do not prove exclusion.
- Review public branding/manifest scope too: public does not mean identical across
  hospital portals. Do not strip query parameters/ignoreSearch globally for fallback.
- For offline navigation, prove the fallback shell contains no wrong-account data or
  wrong-hospital identity. Distinguish shell availability from authenticated API access.
- Verify cached document/CSP/nonce compatibility and matching build chunks; do not
  create blank offline screens by mixing HTML and scripts from incompatible builds.
- Version application caches, clean only namespaces this app owns, and limit size/age.
  Do not delete unrelated same-origin Cache Storage during activation.
- Warmup must use an eligibility allowlist, bounded concurrency/bytes and honest ready
  signaling. A completed warmup message is not proof every required asset was kept.
- Audit dynamic route/RSC/prefetch responses separately from full document navigation;
  don't match one response representation to a different request type.
- Keep delayed registration/warmup from competing with critical first paint unless
  a measured offline-readiness requirement justifies it.
- Preserve update behavior that protects unsaved forms and pending actions. Do not
  force reload/activate a new worker at a moment that loses work.
- Test offline reload and online recovery on the production build, not only next dev.
  Handle storage denial/quota/eviction and memory fallback with truthful messaging.

J. REALTIME, POLLING AND FRESHNESS

- Keep the existing Socket.IO transport and shared domain reducer; do not replace them
  just because a reference app uses another WebSocket library.
- Own each subscription at the appropriate shared feature/page level; deduplicate
  panels subscribing to the same stream where authorization and lifetimes match.
- Stable callbacks/subscription keys must not recreate sockets on every render.
- Respect authoritative sequence/version/timestamps; handle duplicates/out-of-order
  events, gaps, reconnect snapshots and acknowledgement races.
- REST responses and events may arrive in either order. Reconcile them without applying
  one action twice or overwriting a newer state with an older response.
- Keep optimistic pending events separate from confirmed state as the existing design
  requires; generic query updates must not bypass replay/settlement semantics.
- Do not refetch an entire dashboard on every frame. Update/invalidate the smallest
  affected read models, coalescing bursts only within the product's freshness budget.
- Replace duplicate polling with one deliberate owner. Don't overlap polls; add a
  bounded error policy and stop inactive/hidden noncritical work when appropriate.
- Do not pause critical live/offline synchronization merely to cut background network
  requests. Preserve deadlines, gap recovery and the existing live-update canary.
- Keep "last received now" separate from the data's server as-of time. Display missing,
  stale, refreshing, disconnected and unknown data honestly; unknown is not zero.
- Share age/countdown clocks where useful so a long list doesn't create one interval
  per row. Avoid clock-driven rerendering of the entire workspace.
- Cleanup all subscriptions, timers, observers and listeners on context change/unmount;
  recover cleanly from session renewal, screen sleep and rapid navigation.
- Bound accumulated live-history maps, chart points, settled-ID sets and per-resource
  caches by time/count and reconcile evicted state safely. Limiting socket count alone
  doesn't bound memory during a long shift. Never evict unacknowledged durable work
  as if it were disposable chart history.

K. DASHBOARD DESIGN PATTERNS

Use the approved shared console foundation; do not create another competing theme.
Improve composition and reuse while preserving each workspace's actual work.

Shared shell:
- Stable institution/account identity, role/module-aware navigation, current location,
  workspace header, useful page actions and feedback/status region.
- Navigation presentation consumes permitted choices; it is not authorization.
  Protected data/actions still depend on backend checks and existing client guards.
- Avoid mounting a complete shell/provider tree inside every panel or tab.
- Brand/theme scope must include dialogs/portals without leaking into patient/site
  apps. Status colors remain semantic and fixed under hospital brand changes.
- Shared session/branding/options should not flicker or refetch independently in
  header, rail and page. Primary work must remain available if optional branding fails.

Page composition:
  page header/breadcrumb or context -> primary action/filter toolbar
  -> operational summary only when useful -> main work surface -> secondary details.

Choose patterns from the existing workflow:
  summary dashboard -> compact meaningful metrics, age and actionable drilldown;
  management workspace -> search/filter, bounded table, selection and row actions;
  master/detail -> stable list plus detail panel preserving selection/context;
  editing -> explicit form/draft lifecycle, validation, save status and safe navigation;
  live board -> connection/freshness/pending state and authoritative transitions;
  report -> clear units, date boundaries, aggregation meaning and accessible export.

- Do not turn every screen into identical statistic-card grids. Do not invent metrics,
  trends or a success percentage that the API doesn't supply.
- Keep one clear primary action per relevant task area. Secondary and destructive
  actions need distinct weight and useful confirmation when warranted.
- Build reusable DataTable/FilterToolbar/StatePanel/DetailDrawer/FormActions patterns
  only where behavior is truly shared. Prefer composition to a massive conditional
  component with dozens of domain flags.
- Reuse existing ConsoleShell/PageHeader/Panel/Input/Button/Sheet/Toast equivalents.
  Extract proven patterns; don't rename stable primitives merely for uniformity.
- Preserve navigation/back/deep-link contracts, permitted role changes and unsaved
  draft guards. Do not rewrite the current single-route workspace model without need.

L. LOADING, ERROR AND INTERACTION STATES

Specify each feature's states explicitly:
  initial loading; ready; valid empty; filtered empty; refreshing with usable data;
  partial widget failure; initial error; stale/offline; forbidden/session-limited;
  pending action; rejected action; confirmed success; unknown outcome/reconciliation.

- Initial skeletons reserve realistic space and do not delay content already available.
- Background refresh keeps permitted useful data visible with age/error feedback;
  account/hospital transitions must clear unrelated data rather than preserve it.
- Empty results are not a generic error, and a network failure is not "no records".
- A retry acts on the failed resource, not a blanket page reload.
- Keep inputs responsive, show pending feedback, prevent unintended duplicate submits,
  and preserve drafts/focus/scroll/selection during non-destructive refreshes.
- Announce errors and results accessibly without shouting every live tick.
- Distinguish UI success from queued/offline/pending server confirmation.

M. TABLES, FILTERS, FORMS AND CHARTS

- Debounce network-driving search while keeping input state immediate. Cancel/guard
  old searches. Preserve input focus and avoid remount keys tied to typed text.
- Reset page/cursor when filters change; serialize canonical query parameters and
  retain safe shareable state where the routing contract supports it.
- Scope API filter parameters consistently with query identity. A selected hospital
  must never display another hospital's cached table/detail while loading.
- Use existing server pagination/count/options contracts; don't fetch thousands of
  details just to populate a dropdown, table count or client-side filter.
- Retain local filtering for already-small complete datasets when it is the deliberate
  product design; don't introduce unsupported backend filters speculatively.
- Stable row IDs, keyed selection and explicit bulk-action scope; "select all" must
  state whether it means current page or the full permitted filtered result.
- Paginate before considering virtualization. Virtualization is conditional on actual
  render size and must preserve keyboard access, focused controls and row semantics.
- Keep drawer/detail fetching independent from the whole table. Avoid per-row hidden
  modal data requests, and load large details only when needed.
- Keep form drafts separate from refreshed data; an incoming snapshot must not silently
  overwrite edited fields. Conflict/reload behavior follows existing domain requirements.
- Lazy-load optional heavy charts/export/editors. Preserve required instant tab
  switching if its existing bounded shared payload is an intentional contract.
- Charts need clear labels/units/age, readable legends and accessible data alternatives;
  don't rely only on color, heavy decoration or animated counts.
- Measure large imports/exports/parsing before moving them to a Web Worker. Bound files,
  cancel work and avoid exposing sensitive data to third-party processing services.

M1. SEARCHABLE LOOKUPS AND FILTER CONTROLS

- Reuse a genuine shared combobox/resource-lookup pattern rather than separate
  debounce/list/selection implementations in every form.
- Keep selected entity ID separate from typed search text; don't overwrite active
  typing when an unrelated parent refreshes or the selected display label updates.
- Apply minimum characters, bounded options, stable fetcher identity, cancellation,
  generation checks and query/scope-aware reuse. Don't fetch the whole entity table.
- Distinguish searching/no matches/transport error/forbidden states. A lookup failure
  must not become "no matches" or offer to create a duplicate record.
- Keyboard navigation must include the proper combobox/listbox/option semantics,
  active descendant/selection state, Escape and focus behavior. Arrow-key handlers
  alone do not establish an accessible combobox.
- Hidden tabs/components can remain mounted and still run query hooks. Enable reads
  for the active/needed resources, or document intentional bounded preloading for
  instant switching; returning null from rendering alone doesn't stop a request.
- Inline create is conditional on existing permission/API support. Do not invent
  clinical entities or writes from free-form search as a convenience feature.
- Centralize date-range/multi-select/page controls where useful; preserve hospital
  timezone and date-only meaning. Keep their keyboard semantics and query boundary
  validation; don't copy a pointer-only custom calendar because it looks consistent.

M2. FEEDBACK AND DIALOG LIFECYCLE

- Use the existing shared toast/inline feedback system; deduplicate repeated event
  messages, bound visible messages and preserve appropriate announcement priority.
- Keep actionable feedback available long enough; pause transient dismissal while
  hovered/focused when appropriate. Errors needing action belong in persistent inline
  state too. Don't hide a failed save just because its toast timed out.
- Select tone from explicit outcome/error state, not English keyword matching or a
  generic status word whose meaning changes by healthcare workflow.
- Keep persistent job state separate from transient messages. A toast is not job history.
- Reuse existing safe confirmation/dialog primitives; don't replace approved Radix
  behavior with another custom global-event or focus-trap framework.
- Opening a dialog initializes focus once. Fresh inline callbacks or typing must not
  re-run focus setup and jump the cursor to the close button on every keystroke.
- Preserve input/draft while help or secondary details are open. Use stable component
  keys and deliberate reset/open semantics rather than remounting the whole form.
- Guard backdrop/Escape/close behavior while a dangerous write is in flight, with an
  explicit recovery path. Closing the UI does not cancel a server write automatically.
- Nested overlays need coordinated focus, scroll locking, inert/background interaction,
  theme and restoration order. Closing one must not unlock a still-open parent.
- Confirmations authorize a particular requested action; stale selection/scope must not
  silently redirect the confirmed action to another record.

M3. BACKGROUND OPERATIONS AND DOWNLOADS

- Where an existing API already exposes long-running import/export/processing jobs,
  use one shared owner for job history/progress rather than hiding work in each modal.
- Keep the authoritative job ID, owner, states, timestamps and result/error contract.
  Reopen after navigation/reload from the server's permitted job list where supported.
- Show determinate progress only when backend counters justify it. Otherwise show
  indeterminate processing; don't invent percentages or claim completion on enqueue.
- Retry the existing job/operation through its supported idempotency contract, not
  blindly repeat the initial bulk write. Refresh affected resources after completion.
- Poll active work differently from idle history, with no overlap, backoff/error state
  and scope cleanup. Coordinate duplicate consumers. Hidden noncritical monitors can
  pause, but resume/check status on return and preserve required sync behavior.
- A monitor failure must not blank the dashboard; still expose truthful last-known
  state/unavailability instead of silently implying all jobs finished.
- Preserve result permission/expiry checks; download only from the supported endpoint.
- Centralize binary download errors/filenames where useful, clean temporary anchors
  and object URLs, and avoid materializing arbitrarily large exports in the browser.
- Treat filenames/CSV content/result URLs as untrusted presentation data. Do not
  expose patient identifiers through analytics, filenames or persistent cache keys.
- This pattern is optional where supported. Do not add a new jobs backend to satisfy
  a frontend folder pattern.

M4. UPLOADS, MEDIA REFERENCES AND PROCESSING

- Store stable backend attachment/document IDs or references when the existing API
  provides them; signed display URLs are temporary presentation, not durable identity.
- Keep authoritative reference, preview URL, file state and caption/ordering separate.
  Fetch a new authorized URL on expiry; do not keep displaying another account's file.
- Model selected/validating/uploading/uploaded/processing/ready/failed/cancelled states
  only as supported. A completed byte upload does not prove a document is ready for use.
- Client MIME/extension/size validation is feedback, never a substitute for server
  validation. Patient-document rules take precedence over public image convenience.
- Limit upload fan-out and file/batch counts. Preserve successful items on partial
  failure; retry only failed items and keep the same idempotency key for the same
  logical upload when the server supports it. Re-running a helper with new keys is
  not automatically idempotent.
- Preserve cancellation and endpoint-appropriate deadlines; clean object URL previews,
  polling timers and stale file state on close/context change.
- Disable or warn about save/navigation only when unfinished uploads affect validity;
  never leave an action permanently disabled after a failed or cancelled transfer.
- Keep previews/access controlled and image optimization separate from private file
  download. Do not copy public listing video formats/limits into clinical documents.

M5. NAVIGATION, LINKS AND FAIL-CLOSED FALLBACKS

- Validate next/return targets as permitted same-origin application paths; reject
  protocol-relative, backslash/scheme tricks and unsupported destinations. Preserve
  allowed route/query state without creating an open redirect or redirect loop.
- Notification/job links should resolve the intended authorized record/tab after login
  and permission checks, rather than landing on a generic unrelated dashboard page.
- Preserve supported legacy/canonical URL redirects and browser Back behavior; scope
  and filters must not silently disappear when opening a detail and returning.
- If resolving the intended hospital/record/scope fails, show its own retry/error or
  permitted explicit exit. Do not fall back automatically to unfiltered/global data.
- URL state must not expose tokens or sensitive patient search/form content. Shareable
  state and private ephemeral state need different owners.
- Don't invent public SEO/sitemap/canonical metadata for authenticated clinical pages.
  Public site metadata may be optimized independently under its own privacy policy.

N. RENDERING, BUNDLES, ASSETS AND PERCEIVED PERFORMANCE

- Profile before adding memo/useMemo/useCallback. Optimize expensive transformations,
  unstable props and broad context updates; do not sprinkle memoization everywhere.
- Split high-frequency state from shell/preferences so a live row update doesn't
  redraw every dashboard panel. Avoid recomputing large data transforms per clock tick.
- Use dynamic imports for optional heavy UI without delaying the main task surface;
  preserve SSR/accessibility/CSP and predictable loading states for those chunks.
- Inspect bundle dependency graphs and actual chunk loading. Barrel-import optimization
  settings or tree-shaking declarations alone are not proof of a smaller shipped bundle.
- Keep shared domain/offline dependencies out of marketing bundles when unused.
- Preserve workspace transpilation and extension aliases. Do not switch bundlers or
  enable framework/compiler experiments as a side effect of performance cleanup.
- Use appropriately sized images and layout dimensions; reserve space, choose loading
  priority for real above-fold content, and avoid preloading every icon/thumbnail.
- Optimize eligible imagery through the existing image pipeline; retain intentional
  SVG/data/blob/private-auth asset handling. An image optimizer must not bypass access.
- Long asset caching requires stable versioned URLs. New private images must not share
  a public derivative key across identities. Review signed URL lifetime behavior.
- Preserve existing font system, Bangla glyph coverage and typography. Subset/limit
  weights/preloads only when supported; avoid multiple redundant font downloads.
- Do not hide the primary content behind animation/IntersectionObserver initialization.
  Honor reduced motion and keep animations out of critical live/clinical actions.
- Avoid large synchronous transforms, forced layout loops and unbounded DOM growth.

O. ACCESSIBILITY, RESPONSIVENESS AND LOCALIZATION

- Follow existing tokens/design foundation and translation functions. No new arbitrary
  palette/font/radius system or hard-coded UI strings.
- Preserve Bangla-first behavior, English switch, localized numerals, dates/timezones,
  script shaping, required line height and responsive text at 200% zoom.
- Do not import RTL behavior from a reference product into a Bangla/English interface;
  support only the target's required directions/languages correctly.
- Meaningful landmarks/headings, labels, keyboard order, visible focus, skip navigation,
  named icon controls and accessible validation/disabled reasons.
- Dialogs/sheets must trap/restore focus appropriately, support safe dismissal and not
  trigger global workspace shortcuts while a form/help overlay is active.
- Table sorting/selection and status information need programmatic semantics; chart
  and semantic status meaning must not depend on color alone.
- Honor approved desktop/tablet/mobile coverage and touch targets; use a table's own
  overflow region when needed rather than breaking the whole page. Don't disable zoom.
- Preserve distinct console/patient/site styling; opt-in CSS/theme changes must stay
  scoped, including portals and separate hospitals' branding.
- Use real buttons/links with correct behavior. Hide or explain unavailable navigation
  according to existing rules; do not present decorative controls as working features.

- Format display numbers/dates without corrupting entity IDs, codes, serials, phone
  input or machine payloads. Validate locale-specific numeric input separately from
  presentation. A source project's calendar/currency/timezone isn't the target's.
- Theme/locale continuity should survive approved navigation/login transitions without
  wrong-context flashes. Initialize client preferences compatibly with SSR/CSP;
  don't insert unapproved inline scripts merely to hide a hydration mismatch.
- Derive visual status from the owning domain's meaning. For example, an "open" queue
  and an "open" incident need not share a danger tone; avoid one global string map
  silently overriding healthcare semantics.

P. IMPLEMENTATION STAGES

Stage 0 — Inventory and baseline
  Map apps, shared owners, request/caching layers and dashboard patterns. Record
  representative initial/tab/filter/mutation/reconnect request counts and pain points.
  Gate: concrete plan, cache matrix, selected slice and honest baseline failures.

Stage 1 — One representative dashboard slice
  Reuse existing shell/theme; extract data/view hooks and feature presentation while
  preserving all interactions, translations, role checks and test contracts.
  Gate: behavior/accessibility parity and no duplicate state/domain logic.

Stage 2 — Resource identity and request lifecycle
  Standardize scoped keys/owners, deduplicate shared reads, add cancellation/guards and
  session cleanup. Keep offline reducer/outbox ownership untouched.
  Gate: late-response/account-switch/hospital-switch/cross-tab tests and bounded reads.

Stage 3 — Mutation and realtime coherence
  Centralize invalidation/updates, preserve pending actions and eliminate duplicate
  polling/subscriptions. Validate event/REST ordering and reconnect reconciliation.
  Gate: command outcomes, freshness, domain parity and applicable live-update canary.

Stage 4 — Cache Storage/IndexedDB review
  Make caching eligibility, build updates, scope/freshness and persistence rules
  explicit. Preserve intentional offline support and private-data restrictions.
  Gate: production-built offline reload, update, logout/scope and storage-failure tests.

Stage 5 — Rendering and dashboard reuse
  Optimize measured bundle/list/chart/image/font/render problems. Reuse proven toolbar,
  table/form/detail/state patterns across remaining authorized features.
  Gate: meaningful before/after evidence and responsive/accessibility parity.

Stage 6 — Regression and documentation
  Run required app/package checks and dependent browser journeys; document final
  ownership, cache lifecycle, compatibility, measured gains and remaining limits.
  Gate: no broken imports/builds/new failures; no unsupported safety/performance claim.

Use one coherent vertical slice/branch at a time under repository rules. Do not perform
a blind whole-app rewrite or move every component before proving one slice works.

Q. VERIFICATION

Use existing pnpm scripts/configuration and actual installed test tools. On this host
use pnpm.cmd if PowerShell execution policy blocks the .ps1 shim. Run focused tests
first; expand according to changed behavior and the repository's gates.

Candidate checks, selected after inspecting current scripts:
  pnpm.cmd typecheck
  pnpm.cmd lint
  pnpm.cmd format:check
  targeted Vitest unit/UI/resource tests under the existing project configs
  builds for affected console/patient/site packages
  relevant Playwright dev/built/production-config journeys

Do not run fixture/data reset or production commands just for frontend validation.
Do not claim tests collected a new directory unless test include patterns cover it.

Required behavioral coverage for affected paths:
- Shared consumers reuse a read; unrelated scope/filter keys don't collide.
- Slow prior filter/tab/session/hospital response cannot replace newer state.
- Switching identity/scope cannot show/repopulate the previous private data/theme.
- Mutation updates/invalidation and concurrent actions don't lose accepted changes.
- Realtime duplicate/out-of-order/gap/acknowledgement/reconnect behavior stays correct.
- Network error preserves approved offline actions/drafts and shows truthful state.
- Service worker stores only eligible content; offline reload doesn't reuse another
  portal/account/representation/build; updates don't lose pending work.
- Storage blocked/quota/corruption falls back honestly without crashing.
- Widget failure is isolated; primary task and allowed navigation remain usable.
- Keyboard, dialog focus, zoom, locales, approved viewports and semantic colors pass.
- Typing in an open dialog retains focus through parent updates; nested overlays and
  optional help close in the right order without losing draft/selection/scroll.
- Async lookup errors cannot create false "not found"/quick-create states; old searches
  cannot replace the latest result; keyboard semantics are verified.
- Existing job monitoring, downloads and partial uploads preserve IDs/permissions and
  retry semantics through failures, navigation and account/scope changes.
- Safe return links/deep links and missing-scope failures never redirect externally or
  show unfiltered records. Build/hydration/runtime console errors remain absent.

Measure on production builds with synthetic data and representative device/network
conditions. Record initial/navigation/data-ready timing, request count/duplication,
transferred bytes/chunk sizes, render/long-task behavior, layout shifts and applicable
LCP/INP/CLS. Separate lab checks, mocked tests and real-user measurements.

Set budgets from actual workflow requirements. Fewer requests isn't automatically a
win if data becomes stale, queue updates miss deadlines or initial work gets blocked.
No manufactured percentages, unrun benchmark claims or screenshot-only acceptance.

R. FINAL DEFINITION OF DONE

  [ ] App/shared-package responsibilities are clear and imports remain valid.
  [ ] Dashboard shell/pattern reuse preserves approved visuals and real workflows.
  [ ] Each state/cache has one owner, scoped identity and documented lifecycle.
  [ ] No duplicate shell requests, uncontrolled polling or redundant subscriptions.
  [ ] Cancellation/late-response guards and identity cleanup are tested.
  [ ] Mutations, realtime and durable offline actions reconcile without data loss.
  [ ] Cache Storage/Next/query/IndexedDB policies are separate and privacy-aware.
  [ ] Data age, pending/offline/stale/error/unknown states remain honest.
  [ ] Measured rendering/bundle/asset changes improve relevant budgets.
  [ ] Keyboard/zoom/localization/responsive and permission behavior remain correct.
  [ ] Required checks pass; pre-existing failures and unverified claims are recorded.
  [ ] No unintended backend/API/schema/product/dependency/deployment changes.

Report: files/responsibilities changed; dashboard and data-lifecycle behavior improved;
cache policy and identity boundaries; checks actually run; before/after measurements;
remaining limitations and compatibility/rollback notes. Do not claim the frontend is
"perfectly optimized" merely because caching or a query library exists.
````

## 3. References and verification boundaries

Framework semantics were checked against installed Next.js documentation and official references. The proposed folder layout, dashboard composition and staged workflow are architectural recommendations, not framework requirements.

- [TanStack Query defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults) explains freshness, retention and refetch settings if that library is selected.
- [TanStack Query cancellation](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation) explains consuming a query's AbortSignal in the actual transport.
- [Next.js CSP guidance](https://nextjs.org/docs/app/guides/content-security-policy) explains nonce-based dynamic rendering constraints.
- [Next.js Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components) explains rendering boundaries and initial hydration.
- [Next.js caching without Cache Components](https://nextjs.org/docs/app/guides/caching-without-cache-components) explains the applicable fetch/segment model when the feature flag is off.
- [Next.js revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag) and [updateTag](https://nextjs.org/docs/app/api-reference/functions/updateTag) distinguish supported server-side invalidation behaviors.
- [MDN Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache) explains why explicit service-worker storage rules matter independently of HTTP caching headers.

UI guidance was reviewed with the [UI/UX Pro Max skill](C:/Users/ABDULLAH/.codex/skills/ui-ux-pro-max/SKILL.md), using dashboard accessibility and Next.js searches. The target project's approved design takes precedence over generic design suggestions.

This document was validated as a prompt/artifact. No target application refactor, browser benchmark, test suite or production operation was performed while writing it.
