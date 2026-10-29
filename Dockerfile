# syntax=docker/dockerfile:1
# Django API, separate SQL migration tools, and Next.js frontend targets.
# Build the api, database-tools, console or patient target from the repository root.

FROM node:24-bookworm-slim AS base
ENV PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH \
    CI=true \
    NEXT_TELEMETRY_DISABLED=1 \
    # Where corepack keeps the pnpm it fetched. Its default is the home folder
    # of whoever ran it — root's, at build time — and the account the services
    # run as would look in its own, find nothing, and try to download pnpm
    # again on every start.
    COREPACK_HOME=/corepack
RUN corepack enable
WORKDIR /app

# --- the workspace, installed once ---------------------------------------------
FROM base AS deps
COPY . .
RUN pnpm install --frozen-lockfile \
    && chown -R node:node /corepack
# The dependencies were installed and checked against the lockfile when this
# image was built. Left on, pnpm checks them again before every `pnpm run` —
# and to do it re-marks files in node_modules, which the account the services
# run as does not own and may not touch: the first start as that account
# stopped here, before a single migration ran.
ENV pnpm_config_verify_deps_before_run=false

# --- SQL migration tooling (separate from the Python API) ------------------------
FROM base AS database-tools
ENV NODE_ENV=production \
    pnpm_config_verify_deps_before_run=false
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY shared ./shared
COPY database ./database
RUN pnpm install --frozen-lockfile --prod --filter "@platform/database..." \
    && chown -R node:node /corepack
USER node
CMD ["pnpm", "db:migrate"]

# --- Django API, Socket.IO and Python background jobs ---------------------------
FROM python:3.13-slim-bookworm AS api
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=backend.core.settings
WORKDIR /app
COPY backend/requirements.lock.txt ./requirements.lock.txt
RUN pip install -r requirements.lock.txt
COPY backend ./backend
RUN useradd --system --uid 10001 --home /app medlive \
    && mkdir -p /data/files && chown medlive:medlive /data/files
USER medlive
EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4000/readyz', timeout=4)"
CMD ["python", "-m", "uvicorn", "backend.core.asgi:application", "--host", "0.0.0.0", "--port", "4000", "--no-proxy-headers", "--timeout-graceful-shutdown", "20"]

# --- the web apps ----------------------------------------------------------------
FROM deps AS web
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_SOCKET_URL
# The platform's own domain, when it has one: the patient app reads a
# hospital's portal address with it (FR-BRD-07). Empty is the ordinary state.
ARG NEXT_PUBLIC_PLATFORM_DOMAIN=
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_SOCKET_URL=$NEXT_PUBLIC_SOCKET_URL \
    NEXT_PUBLIC_PLATFORM_DOMAIN=$NEXT_PUBLIC_PLATFORM_DOMAIN

FROM web AS console
RUN pnpm --filter @platform/console build \
    && chown -R node:node frontend/console/.next
ENV NODE_ENV=production
USER node
EXPOSE 3100
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3100/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
# `next` itself, as the API's image runs `node` (plan I2): under `pnpm`,
# `docker stop` killed the server rather than closing it. The same command as
# the app's `start` script, from the app's own folder.
WORKDIR /app/frontend/console
CMD ["node", "node_modules/next/dist/bin/next", "start", "--port", "3100"]

FROM web AS patient
RUN pnpm --filter @platform/patient build \
    && chown -R node:node frontend/patient/.next
ENV NODE_ENV=production
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
# As the console's.
WORKDIR /app/frontend/patient
CMD ["node", "node_modules/next/dist/bin/next", "start", "--port", "3000"]
