# MedLiveBD — a national healthcare platform for Bangladesh

This independent `medlivebd` repository retains the consolidated healthcare
codebase and history from source master `0b4d968`: patient PWA, hospital/staff
workspaces, company website, Django API, SQL migrations, realtime/offline flows
and the Django/Python backend. **`master` is the development base.**

The frontend/backend refactor follows both supplied briefs. Start with the
[implementation and verification index](docs/refactor/README.md),
[backend ownership](docs/backend-refactor/CURRENT_STATE.md),
[frontend ownership](docs/frontend-refactor/CURRENT_STATE.md) and
[local development](docs/LOCAL_DEVELOPMENT.md). Historical branch decisions remain
in [the source branch inventory](docs/BRANCH_INTEGRATION.md).

## Start the consolidated app on Windows

Requires Node 22.19+ (24 recommended), Corepack, Python 3.12+ for Django,
and local PostgreSQL 16 with PostGIS (Docker, Ubuntu WSL or an existing instance).

```powershell
git switch master
.\run.ps1 -Preview -Background
# Patient http://localhost:3000 · Staff http://localhost:3100
# Website http://localhost:3200/en (or /bn) · API http://localhost:4000/readyz
.\run.ps1 -Stop
```

The launcher defaults to Django, installs pinned dependencies, generates missing
local secrets, migrates, seeds only an empty database and verifies its schema.
Existing demo data is preserved. Use `-SetupOnly` to prepare without starting, or `-SkipInstall` after dependencies are
installed. Logs and ownership records are in ignored `.local/`. The `-Preview`
option builds and serves production UI bundles against the local synthetic API.
After a verified build, `-Preview -SkipBuild` reuses them. Omit `-Preview` for
hot-reloading frontend development.

On the inspected machine the existing demo database is on **localhost:5433**;
5432 belongs to another instance. The ignored `.env` now selects 5433. Start with:

```powershell
.\run.ps1 -Preview -Background -DatabaseProvider Existing
```

The frontends and browser packages are JavaScript/JSX. Shared domain rules,
translations, database tools and test-only contract references remain TypeScript. Django
uses the existing SQL ledger: do not run Django ORM migrations.

A two-sided healthcare platform: a Bangla-first patient PWA and a set of hospital
staff consoles, built around a **live queue engine** that keeps a doctor's chamber
queue true in real time.

Reception taps _next_; every waiting patient's phone updates within two seconds.
That is the product. Everything else supports it.

## The documents are the source of truth

| Document                             | Authority over                                                          |
| ------------------------------------ | ----------------------------------------------------------------------- |
| [docs/PRD.md](docs/PRD.md)           | Scope and requirements — every requirement has an ID (`FR-QUE-14`)      |
| [docs/APP_FLOW.md](docs/APP_FLOW.md) | Screens, controls and wiring — every control has an ID (`BTN-B02-NEXT`) |
| [docs/FRONTEND.md](docs/FRONTEND.md) | Design system and client architecture                                   |
| [docs/DATABASE.md](docs/DATABASE.md) | Schema, RLS, migration order                                            |
| [docs/BACKEND.md](docs/BACKEND.md)   | Services, files, APIs, realtime, sync, workers                          |

If code and a document disagree, the document wins. Working agreements for this
repository — branch policy, definition of done, testing rules — are in
[CLAUDE.md](CLAUDE.md).

## Layout

```
frontend/      Everything that runs in a browser
  patient/     Patient PWA (Part A)              — Next.js, Bangla-first, installable
  console/     Hospital consoles (Part B)        — Next.js, keyboard-first, offline-first
  site/        Marketing website (Part C)        — Next.js, server-rendered
backend/       Django/Python modular monolith
  core/        settings.py, ASGI, routing and grouped shared infrastructure
  identity/    Authentication and access
  catalog/     Public discovery
  queues/      Queue commands and sessions
  ...          Other business domains, directly inside backend/
testing/       Historical contract references and non-Python test drivers
shared/        Imported by both sides
  domain/      Types, queue event log, reducer, ETA maths — pure, no I/O
  client/      Typed API client, session channel, offline queue
  ui/          Design system: tokens, primitives, signature components
  i18n/        Messages and formatters (bn default, en toggle)
  config/      Shared TypeScript and ESLint configuration
database/      Migrations, seeds, schema scripts
```

Runtime code lives in frontend, backend and shared; schema and test tooling have their own directories.

`shared/domain` owns the browser queue rules. The Python backend's pure rules
live in `backend/domain`; generated parity vectors check that both runtimes
interpret queue events consistently (`FR-QUE-05`). The boundaries are enforced:
`frontend/` cannot import from `backend/` or `database/`, and `shared/domain`
imports nothing at all.

## Getting started

Requires Node 22.19+, Corepack, Python 3.12+ and PostgreSQL with PostGIS.
The database can run locally, in Docker or in WSL.

```bash
corepack enable                 # pnpm version comes from package.json
pnpm install
cp .env.example .env            # then fill in the secrets it names
docker compose up -d            # Postgres 16 + PostGIS on localhost:5432
```

## Commands

```bash
pnpm dev              # every app that has a dev server
pnpm dev:api          # the Django API alone
pnpm dev:django       # alias for the Django API
pnpm dev:site         # company website on :3200
pnpm build
pnpm typecheck
pnpm lint             # includes the architectural boundaries
pnpm format
pnpm test             # unit + api + schema
pnpm verify           # typecheck + lint + format + test, as CI runs them
pnpm test:django      # original API suite against Django (see guide for spy cases)
pnpm test:e2e:django  # browser suite against Django; disposable local DB only
pnpm test:e2e:prod:django # production browser configuration against Django

pnpm db:migrate       # apply pending migrations
pnpm db:verify        # assert the DATABASE.md §0 invariants
```

The shared/UI and schema suites run with `pnpm test`; native backend safety/parity
runs with `pnpm test:backend`. The schema and backend suites require the local test databases. Run one with `pnpm vitest run --project unit`.

`pnpm db:seed`, `pnpm db:reset`, `pnpm dev:patient`, `pnpm dev:console` and
`pnpm test:e2e` are implemented. Browser suites rebuild their configured database
and own their app ports; stop local apps first and use a disposable database as
described in the development guide. CI includes master.

## Toolchain notes

- **pnpm is pinned** by the `packageManager` field, so `corepack enable` gives
  every machine and CI the same version. Do not install it globally at a
  different version.
- **TypeScript is held at 6.x on purpose.** TypeScript 7's native compiler is
  faster, but typescript-eslint does not support it yet, and type-aware lint
  rules — unawaited promises, non-exhaustive switches over the queue event union
  — matter more here than compile speed. One compiler serves both `typecheck`
  and `lint`; revisit when typescript-eslint supports 7.1.
- **`shared/config` owns every tooling decision.** A tsconfig or lint rule
  defined inside an app or package is a bug.

## Boundaries the linter enforces

These are load-bearing, not stylistic:

- `routes → controllers → services → repositories → db`. A controller never
  touches SQL; a repository never emits events or sends notifications.
- SQL exists only in `*.repo.ts`.
- `shared/domain` imports no Node built-in, no database driver and no
  framework, and its queue code may not read the clock or a random number —
  replay determinism is a tested guarantee, not an aspiration.
- The queue reducer is defined once.

## Data and safety

The demo and development databases contain **no real patient data, ever**
(`FR-SEC-08`), all demo content is visibly labelled as demonstration data
(`FR-DEM-07`), and no live figure is ever rendered without its freshness stamp —
when the system does not know, it says so (`FR-OFF-03`, `PRD.md` §3.2).
