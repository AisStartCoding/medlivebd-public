# Frontend validation

Baseline production Django browser 85/85; selected development 80/81 (emergency
tracking timeout, isolated attempt passed); built offline 3/3; exported site 30/30.
The baseline is not wholly green. Logs/screenshots and exact source revision are
linked from ../LOCAL_COPY_VERIFICATION_2026-10-28.md.

Record actual focused/expanded checks, request reuse, cancellation/identity races,
worker cache eligibility/offline tests, before/after build chunk bytes and remaining
limits here as stages finish. Use synthetic data, one worker/zero retries and
restricted test roles. A screenshot, cache object or memo call is not performance
evidence. No percentages or real-user performance claims without measurement.

## Implemented stage evidence

- Shared-client cancellation/deadline/late-response tests: 3/3.
- Both worker policy suites: 10/10 (private/RSC/API bypass, marked CSP shell,
  namespace ownership, waiting updates and failed-warm readiness).
- Branding lifecycle: 2/2; simultaneous shell/rail calls issue one request;
  late data after an identity change is neither returned nor retained.
- Shared client focus including existing session tests: 45 checks overall.
- Full `pnpm verify --maxWorkers=1`: 8,164/8,164, 175 files; types, lint and
  format green. The preceding run was 8,162/8,164: two readiness fixtures mixed
  Node/WSL clocks exactly at hour boundaries. They now use the calculator's clock;
  their focused rerun passed 6/6. The original ten baseline failures are fixed.
- Three new production browser regressions passed at the first checkpoint:
  missing credential, non-overlapping slow read and late read after cancellation.
  That checkpoint was 87/88: the old admin browser test waited for a superseded
  response even though the read now aborts. Its replacement checks request failure
  and verifies the newest displayed range; the final full run is recorded below.

Fresh Next 16.3.8 production builds, fresh browser contexts, service workers blocked,
no account/credential/query string, same unauthenticated root and static-JS measurement:

| Local console entry | Script requests | Decoded JavaScript body bytes |
| --- | --- | --- |
| Original source `0b4d968` | 9 | 2,114,369 |
| Refactor after report splitting | 9 | 2,068,742 |
| Final report + national workspace splitting | 9 | 1,681,777 |

The final reduction is 432,592 decoded bytes (20.5%). Repeated final measurement
returned the same count/bytes. Initially the national dashboard still eagerly
imported Recharts; deferring that workspace as well moves the shared chart code
behind real use. Admin Today stays in the existing shell, and reports preserve
all nine sections, ranges, exports and printing. This is decoded JS body size,
not compressed transfer size, TTFB, LCP/INP/CLS or a real-user performance claim.

Reproduce against a local production console with:

```powershell
node scripts/measure-console.mjs http://localhost:3100
```

Browser screenshots of approved Today desktop/tablet layouts were inspected;
existing token hierarchy, navigation, readable figures and freshness states remain.
The browser suites exercise Bangla/English, accessibility and working controls.
Further final production/development/built/site results follow after completion.

## Expanded checks and development diagnostics

- Full production Django browser gate: **88/88**, zero retries (7.9 minutes).
- Company static export/smoke: **30/30**, including both locales, keyboard/axe,
  responsive layouts, reduced motion and no JavaScript.
- The first expanded development run passed 90/91. A public bed-list mirror
  stayed in loading for its ten-second check while another browser runner was
  active; no backend 500 or wrong count was observed. Eight fresh repetitions of
  that exact ward flow then passed, without changing its assertion or timeout.
  Its bounded technical diagnostics now capture outstanding public/static requests
  and DOM loading counts if it occurs again, without bodies or identifiers.
- A development-only tracking fixture assumed exactly one initial request and
  held every later request; Strict Mode can abort the first mount. It now waits
  for initial readiness before holding a poll, and measures concurrent live reads
  rather than counting cancelled mounts. Production assertions and timeouts remain
  unchanged. The strengthened identity test changes the URL through native history,
  verifying that old credential data disappears without a full page reload.
- Tracking render keys use a numeric context generation, keeping credentials out
  of inspectable React key strings.

`pnpm test:e2e:refactor --trace=off` is the reproducible affected development gate.
It requires an explicit local `E2E_DATABASE_URL` ending in `_test` and uses one
worker, zero retries and its own ignored output directory. The final isolated
result is recorded below. Do not interpret an isolated repetition as proof that
an intermittent development condition is impossible.

Final isolated affected-development gate: **94/94 passed**, one worker, zero
retries, 6.6 minutes. This includes all three tracking regressions, the emergency
burn flow, national dashboard/privacy, booking, doctor/lab, ward mirror/outbox,
offline console, no-show and two-device queue. The ward diagnostic repetitions
also passed 8/8. No timeout or mirror-count assertion was relaxed. The compiled
Node API + console offline reload gate passed **3/3** (57 seconds).

After the final context-key/test-fixture changes, all three tracking cases were
also rerun against built production Django and passed **3/3**. Every workspace
production build passed, including the normal company-site build after its static
export test. Post-change workspace typecheck and full lint passed. Source checkpoint:
`367ae0f`. Fresh generated design captures were archived locally and the approved
tracked reference files restored; the refactor does not replace design evidence.

One final launcher probe of development `/search` returned HTTP 200 but logged
`Invalid or unexpected token` in the browser. APIs passed 7/7; pages passed 7/8
in that attempt, so it is not reported as a successful complete run. Forty fresh
Search contexts (20 with SW enabled and 20 blocked) then rendered without any
browser or script-parse error. Its development-only cause was not established.
The final local handover therefore uses an explicit `-Preview` launcher mode,
serving the verified production UI bundles with the existing local synthetic API.
Normal hot-reload development remains available. Preview can build the workspaces
or reuse a verified build with `-SkipBuild`; its runtime probes are recorded below.

Final launcher verification (28 October 2026): both `-ApiBackend Node` and
`-ApiBackend Django` started successfully with `-Preview -SkipBuild -Background -SkipInstall
-DatabaseProvider Existing`. Each passed **7/7 API** and **8/8 browser-page**
probes, including healthy readiness, public discovery, intended 401 for an
unauthenticated staff request, Socket.IO handshake, patient pages, staff entry
and both company-site languages. No page exceptions, API 500s or failed API
requests were observed. The production-built UI preview with Django is left running in the new copy.
The existing local `healthcare_dev` database on port 5433 was preserved; browser,
API and schema tests used separate disposable test databases.

The preview launcher's automatic build path was also exercised (without
`-SkipBuild`): all workspaces built, Django and all three UI servers started,
and a fresh final probe passed **7/7 APIs + 8/8 pages** with no browser errors,
failed API requests or API 500s. Both backend choices passed the same 15 probes
with reused builds too. PowerShell parsing and launcher-script lint passed.
The final running mode is `-Preview` with Django, on the preserved local demo DB.
