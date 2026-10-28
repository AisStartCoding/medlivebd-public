# Django backend

The default MedLiveBD API is a modular monolith: one Django application, with
business responsibilities grouped under `medlive/modules/`.

## Core and configuration

| Location                     | Responsibility                                                                          |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| `medlive/settings.py`        | Django settings, installed apps, database pool and DRF configuration                    |
| `medlive/core/env.py`        | Validated environment configuration                                                     |
| `medlive/core/`              | Shared authentication, request pipeline, database scope, SQL access, errors and logging |
| `medlive/asgi.py`            | HTTP and Socket.IO application entry point; background job lifecycle                    |
| `medlive/urls.py`            | Django URL entry into the protected request pipeline                                    |
| `medlive/routes/__init__.py` | Ordered composition of domain routes                                                    |
| `medlive/apps.py`            | Django application registration and database initialization                             |
| `medlive/test_settings.py`   | Test configuration                                                                      |

Configuration is part of the `medlive` application; it does not need a separate
settings app. Hospital and platform settings are business responsibilities:

- `medlive/modules/hospital/`: hospital profile, departments, doctors, staff,
  schedules, wards, beds and branding.
- `medlive/modules/platform/`: onboarding, agreements, enabled modules, portals
  and deployment configuration.

Other domains, including identity, catalog, queue, booking, clinical and payments,
live alongside these modules. Views handle HTTP, services coordinate commands
and transactions, and repositories own SQL. `medlive/domain/` contains pure
rules; `medlive/adapters/` contains provider integrations; `medlive/realtime/`
owns the shared Socket.IO transport.

## Run locally

From the repository root:

```powershell
.\run.ps1 -Background -DatabaseProvider Existing
```

The launcher reads the root `.env` and starts Django on port 4000 with the three
frontends. To start only the API after local setup, use
`corepack pnpm dev:django`. See [local development](../../docs/LOCAL_DEVELOPMENT.md)
for dependency setup, preview mode, test databases and stop commands.

SQL migrations in `database/migrations/` own the schema. Use the existing
`db:migrate` command; Django ORM migrations do not manage these tables.
`backend/api/` and `backend/workers/` remain the supported Node compatibility
runtime and contract reference.

The former top-level `medlive/controllers/`, `medlive/services/` and
`medlive/repositories/` folders are obsolete. Their source implementations now
belong to domain modules. Local bytecode leftovers were moved to the ignored
`.local/backend-cleanup-20261028/` archive outside this backend.
