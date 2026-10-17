import type { components } from './schema';
export type Model<K extends keyof components['schemas']> = components['schemas'][K];
export type Dataset = Model<'Dataset'>;
export type Scenario = Model<'Scenario'>;
export type Run = Model<'Run'>;
export type Settings = Model<'Settings'>;
export type Bundle = Model<'EvidenceBundle'>;
const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
let csrf = '';
let workspace = '';
export class ApiError extends Error {
  constructor(public status: number, public data: Model<'Error'>) { super(data.message); }
}
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
const keys = new Map<string, string>();
async function actionKey(path: string, body: BodyInit | undefined) {
  const raw = body instanceof FormData ? await (body.get('file') as File).arrayBuffer() : new TextEncoder().encode(String(body));
  const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', raw))].map(n => n.toString(16).padStart(2, '0')).join('');
  const slot = `liqproof-action:${workspace}:${path}:${digest}`;
  let key = keys.get(slot);
  try { key ||= sessionStorage.getItem(slot) || undefined; } catch { /* Memory fallback for restricted storage. */ }
  if (!key) key = crypto.randomUUID();
  keys.set(slot, key);
  try { sessionStorage.setItem(slot, key); } catch { /* No secrets are persisted. */ }
  return { slot, key };
}
async function request<T>(path: string, method = 'GET', body?: BodyInit, extra: Record<string, string> = {}): Promise<T> {
  const mutation = method !== 'GET';
  const action = mutation ? await actionKey(path, body) : null;
  for (let attempt = 0; ; attempt++) {
    let response: Response;
    try {
      response = await fetch(base + path, { method, credentials: 'include', body, signal: AbortSignal.timeout(30000), headers: { ...(body && !(body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}), ...(mutation ? { 'X-CSRF-Token': csrf, 'Idempotency-Key': action!.key } : {}), ...extra } });
    } catch {
      if (attempt < (mutation ? 1 : 2)) { await sleep(700 * (attempt + 1)); continue; }
      throw new Error('Connection lost. Check that the local backend is running, then try again. The same request key will be reused.');
    }
    if (response.status === 503 && attempt < (mutation ? 1 : 2)) { await sleep(1000 * (attempt + 1)); continue; }
    if (action && response.status !== 503) { keys.delete(action.slot); try { sessionStorage.removeItem(action.slot); } catch { /* Storage is optional. */ } }
    if (!response.ok) {
      let error: Model<'Error'>;
      try { error = await response.json(); } catch { throw new Error(`The server returned HTTP ${response.status}. Please reconnect and try again.`); }
      throw new ApiError(response.status, error);
    }
    if (response.headers.has('X-CSRF-Token')) csrf = response.headers.get('X-CSRF-Token')!;
    return response.status === 204 ? undefined as T : response.json();
  }
}
const json = JSON.stringify;
export const api = {
  async connect() { await request('/local/csrf'); const w = await request<Model<'Workspace'>>('/api/v1/workspace'); if (w.contract_version !== '0.1.0' || w.simulation_only !== true) throw new Error('This workspace needs the supported simulation backend (HTTP 0.1.0).'); workspace = w.workspace_id; return w; },
  logout: () => request<void>('/local/logout', 'POST'),
  upload(file: File) { const data = new FormData(); data.append('file', file); return request<Dataset>('/api/v1/datasets', 'POST', data); },
  dataset: (id: string) => request<Dataset>(`/api/v1/datasets/${encodeURIComponent(id)}`),
  createScenario: (body: Model<'ScenarioCreate'>) => request<Scenario>('/api/v1/scenarios', 'POST', json(body)),
  scenario: (id: string) => request<Scenario>(`/api/v1/scenarios/${encodeURIComponent(id)}`),
  review: (s: Scenario, actor: string) => request<Scenario>(`/api/v1/scenarios/${s.scenario_id}/review`, 'POST', json({ actor_label: actor, acknowledge_fictional_assumptions: true }), { 'If-Match': s.fingerprint }),
  start: (s: Scenario, mode: Model<'RunCreate'>['forecast_mode']) => request<Run>('/api/v1/runs', 'POST', json({ scenario_id: s.scenario_id, policy_ids: ['cash_only', 'fixed_repo'], forecast_mode: mode, adapter_artifact_id: null })),
  run: (id: string) => request<Run>(`/api/v1/runs/${encodeURIComponent(id)}`),
  cancel: (id: string) => request<Run>(`/api/v1/runs/${id}/cancel`, 'POST'),
  metrics: (id: string) => request<Model<'MetricSet'>>(`/api/v1/runs/${id}/metrics`),
  decisions: (id: string, cursor?: string) => request<Model<'DecisionPage'>>(`/api/v1/runs/${id}/decisions?limit=100${cursor ? '&cursor=' + encodeURIComponent(cursor) : ''}`),
  export: (id: string) => request<Bundle>(`/api/v1/runs/${id}/export`),
};
