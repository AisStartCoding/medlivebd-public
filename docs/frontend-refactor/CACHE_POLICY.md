# State/cache policy

| Resource | Owner / identity | Reuse, freshness and invalidation | Persistence / cleanup |
| --- | --- | --- | --- |
| Staff session | existing staffAuth/demo owner; principal/family/hospital/roles | single-flight refresh; clear reads/subscriptions on change | existing session policy; no tokens in telemetry/cache keys |
| Branding | console brand owner; hospital + session generation | bounded public-brand reuse; refresh on saved brand; share concurrent read | existing per-hospital session storage; no private records |
| Admin overview/reports | feature resource hooks; principal/hospital/range | retain same-owner data on refresh failure; source server time; 60s current-view refresh | memory only; detach/abort obsolete reads |
| Queue | existing realtime/domain controller; session + actor | event sequence/replay authoritative; REST/event reconciliation | owner-scoped snapshots/outbox; never an HTTP/SW cache |
| Ward/ER actions | existing feature/offline owners | command idempotency and authoritative settlement | owner-scoped durable outbox; never discard pending actions to clear reads |
| Emergency guest status | emergency feature; guest-link credential, kept out of logs | visible/open only, 5s, no overlap; explicit invalid/failure state | memory only; no private/tokenized document caching |
| Private records/files | existing authorized API | no-store; consent/role rules remain authoritative | no generic memory/SW persistence added |
| Build assets | app service worker; exact origin + fingerprinted URL | immutable versioned assets; bounded app namespace | Cache Storage; exclude API/socket/RSC/private docs |
| Neutral app shell | existing approved offline behavior, origin/portal/build scoped | network-first; exact safe fallback; matching nonce/chunks | explicit shell policy only; updates must preserve pending work |
| Public company pages/assets | site Next static export/server output | public build/HTTP caching; separate from clinical code | no clinical/offline packages pulled into marketing |

HTTP cache, Next route/data/router caches, Cache Storage, in-flight reuse and
IndexedDB are separate systems. Their invalidation is never treated as interchangeable.

## Exact lifecycle rules

Admin reads are memory-only and scoped to token/principal/hospital plus requested
Dhaka date range. A changed identity hides the previous data immediately; changed
ranges keep their loaded `data.range` metadata during pending/error states. Replaced
reads abort, polling skips active reads and hidden tabs, and a read has a 15s deadline.
Each source section retains its own server freshness timestamp. There is no additional
result-cache TTL or mutation retry.

Emergency reads use a 12s deadline and a 5s visible/open-case cadence, skip overlapping
reads, stop on terminal/invalid state and abort on unmount/credential change. A cancel
invalidates the old read generation before the command; an uncertain command reconciles
through GET and is never automatically resent. Branding in-flight entries are removed
when settled and aborted on session changes; persisted branding is public metadata,
per hospital for the tab, refreshed on explicit settings save. Failures are not cached.

Each service worker bounds warm input to 512 entries, keeps at most 128 unique eligible
warm URLs, fetches four at a time and retains at most 192 entries in its own versioned
namespace. Assets are network-first with exact static-path keys; only a development
`v` parameter is canonicalized. No `ignoreSearch` fallback applies to documents/RSC.
The patient document fallback is `/` only; the console's neutral CSR root can also
boot existing UI query choices (`session`, `view`, `login`, `tab`). Tokenized routes
never fall back to another page. HTTP no-store stays intact: a marked neutral root
is an explicit offline-only Cache Storage exception, retaining its own CSP header
and nonce. This is safe only while that server-rendered root stays free of private
state. Portal data stays origin-scoped. Warm readiness requires all eligible critical
files and the marked shell, with a correlated message from the controlling worker.
Updates wait; activation deletes only app-owned caches. Offline stores and pending
writes are separate IndexedDB state and are never evicted by this policy.
