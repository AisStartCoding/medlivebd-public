import { describe, expect, it, vi } from 'vitest';

import {
  ApiClient,
  NetworkError,
  RequestCancelledError,
  RequestTimeoutError,
} from '../api/client.js';

function waitingFetch(_url, { signal }) {
  return new Promise((_resolve, reject) => {
    if (signal.aborted) reject(signal.reason);
    else signal.addEventListener('abort', () => reject(signal.reason), { once: true });
  });
}

const client = (fetchImpl) =>
  new ApiClient({ baseUrl: 'https://example.test', getToken: () => null, fetchImpl });

describe('read cancellation (FR-OFF-01)', () => {
  it('distinguishes intentional cancellation from an offline failure and removes its listener', async () => {
    const controller = new AbortController();
    const remove = vi.spyOn(controller.signal, 'removeEventListener');
    const result = client(waitingFetch).get('/read', { signal: controller.signal });
    controller.abort();
    await expect(result).rejects.toBeInstanceOf(RequestCancelledError);
    expect(remove).toHaveBeenCalledWith('abort', expect.any(Function));
  });

  it('bounds a read and reports a timeout without classifying it as an offline command', async () => {
    const error = await client(waitingFetch)
      .get('/read', { timeoutMs: 5 })
      .catch((failure) => failure);
    expect(error).toBeInstanceOf(RequestTimeoutError);
    expect(error).not.toBeInstanceOf(NetworkError);
  });

  it('rejects an aborted response even when the transport ignores cancellation', async () => {
    const controller = new AbortController();
    const api = client(async () => {
      controller.abort();
      return new Response(JSON.stringify({ ok: true, data: { stale: true } }));
    });
    await expect(api.get('/read', { signal: controller.signal })).rejects.toBeInstanceOf(
      RequestCancelledError,
    );
  });
});
