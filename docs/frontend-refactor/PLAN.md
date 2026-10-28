# Frontend implementation plan

The full brief is preserved in ../refactor/briefs/FRONTEND.md. Existing approved
visuals take precedence over generic design suggestions. No new query library,
bundler, compiler experiment, clinical feature or backend contract is introduced.

1. Extract emergency tracking into a feature owner with cancellation, non-overlap,
   context/generation guards and meaningful loading/error behavior. Preserve the
   five-second visible/open-case poll, safe links and idempotent cancellation.
2. Extend shared ApiClient with optional cancellation/deadlines, distinguishing
   intentional cancellation from offline/network failure. Keep old signatures valid;
   do not turn an uncertain command into an automatic mutation retry.
3. Extract proven admin resource hooks from presentation and coordinate scoped
   branding in-flight reads. Clear/detach prior identity results; retain drafts and
   outboxes. Measure request reuse and stale-response/cancellation behavior.
4. Review both service workers using explicit path/type/representation eligibility,
   app-owned cache namespaces, bounded warmup and safe neutral-shell fallback.
   Preserve CSP, portal identity, private-data exclusions and built offline behavior.
5. Split optional heavy chart code from Today while preserving reports/printing and
   access states. Move domain panels into feature ownership only after one slice
   proves import, responsive, locale and accessibility parity.
6. Record bundle/request/query evidence and run real production/built/development
   flows. Keep honest source timestamps and never equate a smaller folder with a
   measured performance improvement. Update VALIDATION.md after each gate.
