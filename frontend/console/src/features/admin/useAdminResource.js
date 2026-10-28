'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import { RequestCancelledError } from '@platform/client/api';

import { adminApi, failureOf } from '@/lib/admin';

const overview = (token, _range, options) => adminApi.overview(token, options);
const reports = (token, range, options) => adminApi.dashboard(token, range, options);

/** Ephemeral admin reads: identity changes detach data; durable outboxes stay independent (FR-ADM-12). */
function useAdminResource(read, token, days, refreshMs) {
  const [resource, setResource] = useState({
    owner: token,
    data: null,
    state: 'loading',
    pending: true,
  });
  const active = useRef(null);
  const latest = useRef(0);
  const load = useCallback(
    async (range = days, replace = true) => {
      if (active.current !== null && !replace) return;
      active.current?.abort();
      const controller = new AbortController();
      active.current = controller;
      const generation = ++latest.current;
      setResource((previous) => ({
        owner: token,
        data: previous.owner === token ? previous.data : null,
        state: previous.owner === token ? previous.state : 'loading',
        pending: true,
      }));
      try {
        const data = await read(token, range, { signal: controller.signal, timeoutMs: 15_000 });
        if (generation === latest.current)
          setResource({ owner: token, data, state: 'ready', pending: false });
      } catch (error) {
        if (generation !== latest.current || error instanceof RequestCancelledError) return;
        setResource((previous) => ({ ...previous, state: failureOf(error), pending: false }));
      } finally {
        if (active.current === controller) active.current = null;
      }
    },
    [token, days, read],
  );

  useEffect(() => {
    void load();
    const timer =
      refreshMs === null
        ? undefined
        : setInterval(() => {
            if (document.visibilityState === 'visible') void load(days, false);
          }, refreshMs);
    return () => {
      latest.current += 1;
      active.current?.abort();
      active.current = null;
      clearInterval(timer);
    };
  }, [load, days, refreshMs]);

  return resource.owner === token
    ? { ...resource, load }
    : { data: null, state: 'loading', pending: true, load };
}

export function useAdminOverview(token) {
  return useAdminResource(overview, token, 0, 60_000);
}

export function useAdminReports(token, days, daily) {
  return useAdminResource(reports, token, days, daily ? 60_000 : null);
}
