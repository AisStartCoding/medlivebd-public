# Python backend

MedLiveBD runs one Django/DRF application with Socket.IO and Python background
jobs. Each business domain is directly inside `backend/`.

```text
backend/
  manage.py
  cli.py
  core/
    settings.py           Django settings and installed apps
    test_settings.py      Synthetic test configuration
    env.py                Environment validation
    asgi.py               HTTP, Socket.IO and job lifecycle
    urls.py               Protected Django HTTP entry
    routes.py             Ordered domain route composition
    apps.py               Django application registration
    security/             Authentication, principals, tokens, passwords and TOTP
    database/             Scoped SQL connections and transactions
    http/                 Request pipeline, routing, errors and rate limits
    validation/           Input schemas and request validation
    observability/        Safe logging and request SQL metrics
    testing/              Restricted test-only integration seam
  identity/
  catalog/
  queues/
  booking/
  clinical/
  beds/
  emergency/
  referrals/
  laboratory/
  hospital/
  platform_admin/
  reporting/
  imports/
  payments/
  messaging/
  demo/
  operations/
  domain/                 Shared pure business rules
  adapters/               Storage, SMS, payments and mapping providers
  realtime/               Socket.IO transport and room authorization
  tests/                  Native Python safety, API and parity tests
  env/                    Checked-in synthetic test environment
  requirements.txt
  requirements.lock.txt
  pyproject.toml
  Dockerfile
```

Domains own their routes, HTTP views, services and SQL repositories. Settings
for a hospital belong to `hospital/`; platform administration belongs to
`platform_admin/`. The `queues` and `platform_admin` names avoid shadowing
Python's standard `queue` and `platform` modules.

## Local commands

From the repository root:

```powershell
.\run.ps1 -Preview -Background -SkipInstall -DatabaseProvider Existing
corepack pnpm dev:api
corepack pnpm test:backend
corepack pnpm staff:create --help
```

The launcher reads the root `.env` and starts the API plus the three frontends.
The backend-only development command uses the same local settings. Direct Python
commands run from the repository root with `backend/.venv/Scripts/python` on
Windows or `backend/.venv/bin/python` elsewhere:

```text
python -m backend.manage check
python -m uvicorn backend.core.asgi:application --port 4000 --no-proxy-headers
python -m backend.cli --help
```

Direct Python startup reads `backend/.env` unless variables were already supplied.
Secrets remain outside version control. SQL migrations in `database/migrations/`
own the schema; use the existing `db:migrate` command, not Django ORM migrations.

The retired Node API server and workers are removed from this backend. Historical
contract tests, reference helpers and browser fixtures live under `testing/`;
they are not another backend runtime. See [test tooling](../testing/README.md) and
[local development](../docs/LOCAL_DEVELOPMENT.md).
