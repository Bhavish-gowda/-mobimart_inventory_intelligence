import React, { useEffect, useState } from 'react';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../api/client';
import type { InventoryRecord, Store, Product } from '../types';
import { LoadingState } from '../components/Common/LoadingState';
import { ErrorState } from '../components/Common/ErrorState';
import { EmptyState } from '../components/Common/EmptyState';

export const InventoryPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [records, setRecords] = useState<InventoryRecord[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 50;

  const [stores, setStores] = useState<Record<string, Store>>({});
  const [products, setProducts] = useState<Record<string, Product>>({});

  const [storeFilter, setStoreFilter] = useState('');
  const [productFilter, setProductFilter] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('');
  const [lifecycleFilter, setLifecycleFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchReferenceData = async () => {
    try {
      const [stRes, prRes] = await Promise.all([api.getStores(), api.getProducts()]);
      const stMap: Record<string, Store> = {};
      stRes.stores.forEach((s) => (stMap[s.id] = s));
      setStores(stMap);

      const prMap: Record<string, Product> = {};
      prRes.products.forEach((p) => (prMap[p.id] = p));
      setProducts(prMap);
    } catch (e) {
      console.error('Failed to load reference metadata', e);
    }
  };

  const fetchInventory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getInventory(
        storeFilter || undefined,
        productFilter || undefined,
        page,
        pageSize
      );
      setRecords(res.records);
      setTotalCount(res.count);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch inventory positions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReferenceData();
  }, []);

  useEffect(() => {
    fetchInventory();
  }, [page, storeFilter, productFilter]);

  // In-memory filter for search, segment, lifecycle
  const filteredRecords = records.filter((r) => {
    const pr = products[r.product_id];
    const st = stores[r.store_id];

    if (segmentFilter && pr?.segment.toLowerCase() !== segmentFilter.toLowerCase()) return false;
    if (lifecycleFilter && pr?.lifecycle_stage.toLowerCase() !== lifecycleFilter.toLowerCase()) return false;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchStore = st?.name.toLowerCase().includes(q) || r.store_id.toLowerCase().includes(q);
      const matchProd = pr?.model_name.toLowerCase().includes(q) || r.product_id.toLowerCase().includes(q);
      if (!matchStore && !matchProd) return false;
    }
    return true;
  });

  const getStatusBadge = (rec: InventoryRecord) => {
    const pr = products[rec.product_id];
    const woc = rec.weeks_of_cover || 0;

    if (pr?.lifecycle_stage === 'EOL') {
      return <span className="badge badge-red">EOL Risk</span>;
    }
    if (rec.current_stock === 0) {
      return <span className="badge badge-red">Stockout</span>;
    }
    if (woc < 1.5) {
      return <span className="badge badge-amber">Low Stock</span>;
    }
    if (woc > 6.0) {
      return <span className="badge badge-amber">Watch (Overstock)</span>;
    }
    return <span className="badge badge-green">Healthy</span>;
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em' }}>
            Store Inventory Positions
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Showing {filteredRecords.length} of {totalCount} store-product positions across Karnataka network
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', alignItems: 'center' }}>
          {/* Search */}
          <div style={{ position: 'relative' }}>
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search store or product..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-text"
              style={{ paddingLeft: '32px', width: '100%' }}
            />
          </div>

          {/* Store Filter */}
          <div>
            <select
              value={storeFilter}
              onChange={(e) => {
                setStoreFilter(e.target.value);
                setPage(1);
              }}
              className="input-select"
              style={{ width: '100%' }}
            >
              <option value="">All Stores (25)</option>
              {Object.values(stores).map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.id})
                </option>
              ))}
            </select>
          </div>

          {/* Product Filter */}
          <div>
            <select
              value={productFilter}
              onChange={(e) => {
                setProductFilter(e.target.value);
                setPage(1);
              }}
              className="input-select"
              style={{ width: '100%' }}
            >
              <option value="">All Products (60)</option>
              {Object.values(products).map((p) => (
                <option key={p.id} value={p.id}>
                  {p.model_name} ({p.id})
                </option>
              ))}
            </select>
          </div>

          {/* Segment Filter */}
          <div>
            <select value={segmentFilter} onChange={(e) => setSegmentFilter(e.target.value)} className="input-select" style={{ width: '100%' }}>
              <option value="">All Segments</option>
              <option value="Budget">Budget</option>
              <option value="Mid-Range">Mid-Range</option>
              <option value="Premium">Premium</option>
              <option value="Flagship">Flagship</option>
            </select>
          </div>

          {/* Lifecycle Filter */}
          <div>
            <select value={lifecycleFilter} onChange={(e) => setLifecycleFilter(e.target.value)} className="input-select" style={{ width: '100%' }}>
              <option value="">All Lifecycle Stages</option>
              <option value="Launch">Launch</option>
              <option value="Growth">Growth</option>
              <option value="Peak">Peak</option>
              <option value="Decline">Decline</option>
              <option value="EOL">EOL</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table Area */}
      {loading ? (
        <LoadingState message="Loading inventory positions from FastAPI..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchInventory} />
      ) : filteredRecords.length === 0 ? (
        <EmptyState message="No inventory positions match your selected filters." />
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Store</th>
                  <th>City</th>
                  <th>Product SKU</th>
                  <th>Segment</th>
                  <th>Lifecycle</th>
                  <th style={{ textAlign: 'right' }}>Stock Units</th>
                  <th style={{ textAlign: 'right' }}>Weeks Cover</th>
                  <th style={{ textAlign: 'right' }}>Unit Cost</th>
                  <th style={{ textAlign: 'right' }}>Total Cost Value</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((r) => {
                  const st = stores[r.store_id];
                  const pr = products[r.product_id];
                  const val = r.current_stock * (pr?.cost_price || 0);

                  return (
                    <tr key={`${r.store_id}-${r.product_id}`}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'white' }}>{st?.name || r.store_id}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{r.store_id}</div>
                      </td>
                      <td>{st?.city || '-'}</td>
                      <td>
                        <div style={{ fontWeight: 600, color: 'white' }}>{pr?.model_name || r.product_id}</div>
                        <div style={{ fontSize: '0.75rem', color: '#38bdf8' }}>{r.product_id}</div>
                      </td>
                      <td>
                        <span className="badge badge-blue">{pr?.segment || '-'}</span>
                      </td>
                      <td>
                        <span className={`badge badge-${pr?.lifecycle_stage === 'EOL' ? 'red' : 'amber'}`}>{pr?.lifecycle_stage || '-'}</span>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 700, color: r.current_stock === 0 ? '#f87171' : 'white' }}>
                        {r.current_stock}
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>
                        {r.weeks_of_cover !== undefined && r.weeks_of_cover !== null ? r.weeks_of_cover.toFixed(1) : '-'} wks
                      </td>
                      <td style={{ textAlign: 'right' }}>₹{(pr?.cost_price || 0).toLocaleString('en-IN')}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600, color: '#34d399' }}>
                        ₹{val.toLocaleString('en-IN')}
                      </td>
                      <td>{getStatusBadge(r)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', backgroundColor: '#0f172a' }}>
            <div style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
              Page {page} of {totalPages} ({totalCount} total positions)
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="btn btn-secondary"
                style={{ padding: '6px 12px' }}
              >
                <ChevronLeft size={16} /> Previous
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="btn btn-secondary"
                style={{ padding: '6px 12px' }}
              >
                Next <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
