# Rendering and cache map

| Surface | Rendering/critical data | Browser-only work | Cache/security choice |
| --- | --- | --- | --- |
| Console entry/workspaces | dynamic nonce-bearing shell; role-gated resource reads | session, live channels, forms, Dexie/outbox | no private shared RSC cache; neutral-shell offline policy only |
| Admin Today | shared shell + critical overview/current report | 60s refresh, age clocks, filters | scoped memory; optional charts separated from primary work |
| Admin Reports | same shell + bounded dated report bundle | charts, export/print, period selection | retain loaded range truthfully; private reads not persisted |
| Patient discovery/booking | dynamic shell, public discovery and supported guest flow | hospital scope, forms, payment/guest navigation | public operational data keeps source age; commands not cached |
| Emergency tracking | dynamic request/route, credential-owned status | visible/open-case poll and safe cancellation | no token/private SSR caching; meaningful initial/loading state |
| Patient records/live serial | dynamic scoped shell | auth/consent, realtime, owner snapshots where approved | no-store API and no generic SW file/document cache |
| Company site | existing public server/static export | optional noncritical motion | public SEO/assets; reduced-motion/no-JS content retained |

Cache Components/partial prerendering are not enabled. Existing dynamic CSP and
workspace extension aliases are retained. Lab bundle/request measurements belong
in VALIDATION.md; they are not field LCP/INP/CLS measurements.

Framework compatibility: installed Next 16.3.8 uses webpack, React 19.3 and existing
dynamic nonce layouts. This package did not include the `dist/docs/` suggested by
its AGENTS file, so official [lazy loading](https://nextjs.org/docs/app/guides/lazy-loading),
[loading conventions](https://nextjs.org/docs/app/api-reference/file-conventions/loading)
and [CSP guidance](https://nextjs.org/docs/app/guides/content-security-policy) were
checked as a fallback. The published docs currently label a newer 16.x release;
no newer cache/compiler features were adopted. Actual compatibility is checked by
this installed version's builds and browser runs.
