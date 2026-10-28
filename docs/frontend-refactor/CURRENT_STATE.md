# Frontend baseline

The existing console, patient and site apps remain separate Next.js 16.3.8 projects
with JavaScript/JSX, webpack extension aliases, shared packages and approved tokens.
The patient/console use request CSP nonces and dynamic layouts. Their browser-owned
sessions, reducer/realtime controllers and Dexie outboxes are not server query caches.
No TanStack Query is installed or needed merely for organization.

Observed gaps: ApiClient has no caller AbortSignal/deadline; repeated resource
lifecycles live in components; admin reports eagerly import Recharts; branding is
kept by hospital but simultaneous readers are not coordinated. Both service workers
cache broad same-origin successful GETs, delete unrelated cache namespaces, and
activate updates immediately. Console offline shell support must remain intact.

The emergency tracking route owns its polling in the page and reads the URL in an
effect. The development audit observed one blank-main hydration/navigation timeout;
an isolated rerun passed. Do not call that fixed by a loading placeholder alone.

Baseline UI evidence: original and copy each passed 7 API/8 page probes; production
85/85; selected development 80/81; built offline 3/3; exported site 30/30. The existing
design, translations, keyboard/focus and clinical semantics are retained.

## Implemented owners

- `patient/src/features/emergency/`: tracking screen and read/command lifetime;
  the route composes Suspense/loading and remounts the credential owner when the
  URL credential changes. Missing credentials show the existing invalid-link UI.
- `console/src/features/admin/`: overview/reports, scoped request hooks, report
  primitives and lazy chart code. `AdminDashboard` retains shell, navigation and
  the existing single management provider. Today does not request chart code.
- `shared/client` exports `./api` for transport-only consumers. Optional read
  cancellation/deadlines distinguish cancellation/timeout from offline failure;
  old call signatures and durable command/outbox semantics remain available.
- `console/src/lib/brand.js`: one in-flight read per hospital/session, ten-second
  deadline and late-identity rejection. Public per-hospital session branding remains
  available offline. Saved-brand refresh still goes through the existing refresh key.
- Each app owns its SW cache namespace, neutral document marker and lifecycle.
  It caches only allowlisted assets and a marked canonical root, excludes private/
  RSC/API/socket content, bounds warmup/storage, verifies readiness and waits for
  clients to close before updating. No IndexedDB outbox or draft is cleared.

No visual redesign, healthcare behavior, translation or new query dependency was
introduced. The rest of the working feature components retain their existing owners;
there is no bulk folder rename or new competing state manager.
