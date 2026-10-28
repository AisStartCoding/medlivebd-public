'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import { ApiError, RequestCancelledError } from '@platform/client/api';

import { cancelEmergency, trackEmergency } from '@/lib/api';

/** One visible, open-case read at a time; old reads cannot undo cancellation (FR-PAT-46). */
export function useEmergencyTracking(token) {
  const [loaded, setLoaded] = useState({ state: 'loading' });
  const [cancelling, setCancelling] = useState(false);
  const active = useRef(null);
  const generation = useRef(0);
  const mounted = useRef(false);
  const mutating = useRef(false);

  const stop = useCallback(() => {
    generation.current += 1;
    active.current?.abort();
    active.current = null;
  }, []);

  const reload = useCallback(async () => {
    if (!token || active.current !== null || mutating.current) return;
    const controller = new AbortController();
    active.current = controller;
    const ownGeneration = generation.current;
    try {
      const status = await trackEmergency(token, { signal: controller.signal, timeoutMs: 12_000 });
      if (mounted.current && ownGeneration === generation.current)
        setLoaded({ state: 'ready', status });
    } catch (error) {
      if (
        !mounted.current ||
        ownGeneration !== generation.current ||
        error instanceof RequestCancelledError
      )
        return;
      const status = error instanceof ApiError ? error.status : null;
      setLoaded((current) =>
        [400, 401, 404, 410].includes(status)
          ? { state: 'invalid' }
          : current.state === 'ready'
            ? current
            : { state: 'failed' },
      );
    } finally {
      if (active.current === controller) active.current = null;
    }
  }, [token]);

  useEffect(() => {
    mounted.current = true;
    setLoaded({ state: token === '' ? 'invalid' : 'loading' });
    void reload();
    return () => {
      mounted.current = false;
      stop();
    };
  }, [token, reload, stop]);

  const settled =
    loaded.state === 'ready' && !['inbound', 'acknowledged'].includes(loaded.status.state);
  useEffect(() => {
    if (!token || settled || loaded.state === 'invalid') return undefined;
    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') void reload();
    }, 5_000);
    return () => clearInterval(timer);
  }, [token, settled, loaded.state, reload]);

  const cancel = useCallback(async () => {
    if (!token || mutating.current) return;
    stop();
    const ownGeneration = generation.current;
    mutating.current = true;
    setCancelling(true);
    try {
      const status = await cancelEmergency(token);
      if (mounted.current && ownGeneration === generation.current)
        setLoaded({ state: 'ready', status });
    } catch {
      // A command is not automatically retried: reconcile through a read.
      mutating.current = false;
      if (mounted.current && ownGeneration === generation.current) await reload();
    } finally {
      mutating.current = false;
      if (mounted.current && ownGeneration === generation.current) setCancelling(false);
    }
  }, [token, stop, reload]);

  return { loaded, reload, cancel, cancelling };
}
