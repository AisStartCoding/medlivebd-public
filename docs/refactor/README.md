# MedLiveBD implementation index

This work targets `V:\STARTUP\medlivebd`, copied from the consolidated
`HealthCare` master. It preserves the complete product and its authoritative
requirements, supported Node runtime, SQL ledger and synthetic demo setup.

- Supplied briefs: [backend](briefs/BACKEND.md), [frontend](briefs/FRONTEND.md).
- Backend: [ownership/current state](../backend-refactor/CURRENT_STATE.md),
  [stages/rollback](../backend-refactor/PLAN.md), [validation](../backend-refactor/VALIDATION.md).
- Frontend: [ownership/current state](../frontend-refactor/CURRENT_STATE.md),
  [stages/rollback](../frontend-refactor/PLAN.md), [cache policy](../frontend-refactor/CACHE_POLICY.md),
  [rendering](../frontend-refactor/RENDERING_AND_CACHE_MAP.md), [validation](../frontend-refactor/VALIDATION.md).
- Run/setup: [local development](../LOCAL_DEVELOPMENT.md), root `run.ps1`.
- Comparison baseline: [local-copy audit](../LOCAL_COPY_VERIFICATION_2026-10-28.md),
  [source branch inventory](../BRANCH_INTEGRATION.md).

The implementation has separate correctness, backend and frontend checkpoints.
No schema conversion, dependency upgrade, new clinical feature or live integration
was introduced. Eleven obsolete root exit/interruption files were archived locally
and removed; source requirements, design references, tests, seeds, migrations and
historical audits remain. `.env`, dependencies, build output and local diagnostic
artifacts stay ignored.

Acceptance is the recorded test/build/runtime evidence, not a claim that any software
can be perfect. Live provider credentials, production deployment and field performance
measurement remain separate operational work. This task creates a private source
repository and does not deploy the public application.

## Final acceptance evidence

| Check | Result |
| --- | --- |
| Core verification (types/lint/format/Node API/schema/shared UI/domain) | 8,164/8,164 |
| Native Django safety/parity/boundaries | 233/233 |
| Selected Django workflow contracts | 345/345 |
| Full Django cross-runtime diagnostic | 1,926/1,936; same 10 Node-process spy mismatches, native equivalents pass |
| Production Django browser | 88/88 |
| Affected development browser | 94/94, one worker, zero retries |
| Compiled Node API + offline console | 3/3 |
| Final production tracking lifecycle | 3/3 |
| Company static export/smoke | 30/30 |
| All workspace production builds | Passed |
| Final typecheck and full lint | Passed |

The console entry measured 432,592 fewer decoded JavaScript bytes (20.5%), with
nine script requests in both versions. Targeted doctor reads fetch one doctor
instead of forty on the measured fixture; response size and query count stay the
same. These are local measurements, with scope and limitations in the validation
files. Source checkpoints: correctness `86af592`, backend `9719bba`, frontend
`367ae0f`. No private record cache, speculative index or new dependency was added.

A development bed-list stall was not reproduced in eight fresh repetitions and
passed in the final isolated 94-case run. Its diagnostics remain available; the
report does not claim intermittent development behavior is impossible. Windows
may log asyncio connection-reset callbacks when browser websocket clients close;
those did not fail the passing functional checks. The source is verified in its
approved synthetic/demo mode; provider activation and public deployment remain
separate from this private repository task.

## Run the local copy

The final launcher check passed 15/15 probes with Node and 15/15 with Django.
The new copy is left running as a production-built local UI preview with Django:

- Patient: <http://localhost:3000>
- Staff: <http://localhost:3100>
- Company site: <http://localhost:3200/en> or `/bn`
- API readiness: <http://localhost:4000/readyz>

```powershell
Set-Location V:\STARTUP\medlivebd
.\run.ps1 -Preview -Background -SkipInstall -DatabaseProvider Existing
.\run.ps1 -Stop
```

Local database: the existing synthetic demo at localhost:5433. Do not run the
original checkout on these same app ports simultaneously. The launcher preserves
existing demo data; the explicitly selected `_test` databases belong to test runs.
Use `-ApiBackend Node` after stopping if the supported Node runtime is needed.
No secrets, local logs, dependency folders or build output are published.

The preview build-and-start path (without `-SkipBuild`) was verified too: all
workspaces built and the fresh Django preview passed all 15 probes. This is the
mode left running for the handover. The private `origin` is
<https://github.com/AisStartCoding/medlivebd>; the original source is retained as
`upstream`, and its working tree was verified clean.
