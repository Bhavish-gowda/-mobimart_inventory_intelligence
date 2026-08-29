import type {
  HealthResponse,
  StoreListResponse,
  Store,
  ProductListResponse,
  Product,
  InventoryListResponse,
  InventorySummary,
  ForecastRequest,
  ForecastResponse,
  AllocationRunRequest,
  AllocationRunResponse,
  EOLRiskPortfolioResponse,
  EOLRiskAssessment,
  SimulationRunResult,
  BenchmarkResponse,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}: ${res.statusText}`;
    try {
      const errData = await res.json();
      if (errData?.error?.message) {
        errorMsg = errData.error.message;
      }
    } catch {
      // JSON parsing error ignored
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

async function fetchWithMeta<T>(
  url: string,
  options?: RequestInit,
): Promise<{ data: T; cacheHit: boolean }> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}: ${res.statusText}`;
    try {
      const errData = await res.json();
      if (errData?.error?.message) errorMsg = errData.error.message;
    } catch { /* ignored */ }
    throw new Error(errorMsg);
  }

  const cacheHit = res.headers.get('X-Benchmark-Cache') === 'HIT';
  const data: T = await res.json();
  return { data, cacheHit };
}

export const api = {
  // Health
  getHealth: () => fetchJson<HealthResponse>('/api/v1/health'),
  getReadiness: () => fetchJson<{ status: string; data_loaded: boolean }>('/api/v1/health/ready'),

  // Stores
  getStores: (city?: string, location_type?: string) => {
    const params = new URLSearchParams();
    if (city) params.append('city', city);
    if (location_type) params.append('location_type', location_type);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<StoreListResponse>(`/api/v1/stores${query}`);
  },
  getStoreById: (storeId: string) => fetchJson<Store>(`/api/v1/stores/${storeId}`),

  // Products
  getProducts: (segment?: string, lifecycle_stage?: string) => {
    const params = new URLSearchParams();
    if (segment) params.append('segment', segment);
    if (lifecycle_stage) params.append('lifecycle_stage', lifecycle_stage);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<ProductListResponse>(`/api/v1/products${query}`);
  },
  getProductById: (productId: string) => fetchJson<Product>(`/api/v1/products/${productId}`),

  // Inventory
  getInventory: (storeId?: string, productId?: string, page?: number, pageSize?: number) => {
    const params = new URLSearchParams();
    if (storeId) params.append('store_id', storeId);
    if (productId) params.append('product_id', productId);
    if (page) params.append('page', page.toString());
    if (pageSize) params.append('page_size', pageSize.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<InventoryListResponse>(`/api/v1/inventory${query}`);
  },
  getInventorySummary: () => fetchJson<InventorySummary>('/api/v1/inventory/summary'),

  // Forecast
  generateForecast: (req: ForecastRequest) =>
    fetchJson<ForecastResponse>('/api/v1/forecast', {
      method: 'POST',
      body: JSON.stringify(req),
    }),

  // Allocation
  runAllocation: (req: AllocationRunRequest) =>
    fetchJson<AllocationRunResponse>('/api/v1/allocation/run', {
      method: 'POST',
      body: JSON.stringify(req),
    }),

  // EOL
  getEolRiskPortfolio: (currentWeek = 24, minRiskLevel = 'MEDIUM') => {
    const params = new URLSearchParams({
      current_week: currentWeek.toString(),
      min_risk_level: minRiskLevel,
    });
    return fetchJson<EOLRiskPortfolioResponse>(`/api/v1/eol/risk?${params.toString()}`);
  },
  assessEolPosition: (storeId: string, productId: string, currentWeek = 24) =>
    fetchJson<EOLRiskAssessment | null>('/api/v1/eol/assess', {
      method: 'POST',
      body: JSON.stringify({
        store_id: storeId,
        product_id: productId,
        current_week: currentWeek,
      }),
    }),

  // Simulation
  runSimulation: (strategyName: 'BASELINE' | 'MOBIMART', startWeek = 1, endWeek = 52) =>
    fetchJson<SimulationRunResult>('/api/v1/simulation/run', {
      method: 'POST',
      body: JSON.stringify({
        strategy_name: strategyName,
        config: {
          start_week: startWeek,
          end_week: endWeek,
          capital_budget_limit: 40000000.0,
        },
      }),
    }),

  runBenchmark: (startWeek = 1, endWeek = 52) => {
    const params = new URLSearchParams({
      start_week: startWeek.toString(),
      end_week: endWeek.toString(),
    });
    return fetchWithMeta<BenchmarkResponse>(`/api/v1/simulation/benchmark?${params.toString()}`, {
      method: 'POST',
    });
  },
};
