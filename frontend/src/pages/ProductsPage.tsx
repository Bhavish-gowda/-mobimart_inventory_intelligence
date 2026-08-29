import React, { useEffect, useState } from 'react';
import { Search, Eye, TrendingUp, Cpu } from 'lucide-react';
import { api } from '../api/client';
import type { Product } from '../types';
import { LoadingState } from '../components/Common/LoadingState';
import { ErrorState } from '../components/Common/ErrorState';
import { ForecastModal } from '../components/ForecastModal';

interface ProductsPageProps {
  planningWeek: number;
}

export const ProductsPage: React.FC<ProductsPageProps> = ({ planningWeek }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [segmentFilter, setSegmentFilter] = useState('');
  const [lifecycleFilter, setLifecycleFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showForecastModal, setShowForecastModal] = useState(false);
  const [forecastProductSku, setForecastProductSku] = useState<string | null>(null);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getProducts(segmentFilter || undefined, lifecycleFilter || undefined);
      setProducts(res.products);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch products catalog');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [segmentFilter, lifecycleFilter]);

  const filteredProducts = products.filter((p) => {
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return p.model_name.toLowerCase().includes(q) || p.id.toLowerCase().includes(q) || p.brand?.toLowerCase().includes(q);
    }
    return true;
  });

  const getLifecycleBadge = (stage: string) => {
    switch (stage) {
      case 'Launch':
        return <span className="badge badge-blue">Launch</span>;
      case 'Growth':
        return <span className="badge badge-green">Growth</span>;
      case 'Peak':
        return <span className="badge badge-green">Peak</span>;
      case 'Decline':
        return <span className="badge badge-amber">Decline</span>;
      case 'EOL':
        return <span className="badge badge-red">EOL Risk</span>;
      default:
        return <span className="badge badge-blue">{stage}</span>;
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em' }}>
          Smartphone Catalog Intelligence
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Active product matrix across Budget, Mid-Range, Premium & Flagship tiers (60 SKUs)
        </p>
      </div>

      {/* Filters Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search model, SKU, or brand..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-text"
              style={{ paddingLeft: '32px', width: '100%' }}
            />
          </div>

          <div>
            <select value={segmentFilter} onChange={(e) => setSegmentFilter(e.target.value)} className="input-select" style={{ width: '100%' }}>
              <option value="">All Segments</option>
              <option value="Budget">Budget</option>
              <option value="Mid-Range">Mid-Range</option>
              <option value="Premium">Premium</option>
              <option value="Flagship">Flagship</option>
            </select>
          </div>

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

      {/* Table */}
      {loading ? (
        <LoadingState message="Loading catalog SKUs..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchProducts} />
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>SKU ID</th>
                  <th>Brand & Model Name</th>
                  <th>Market Segment</th>
                  <th>Lifecycle Stage</th>
                  <th style={{ textAlign: 'right' }}>Cost Price</th>
                  <th style={{ textAlign: 'right' }}>Retail Price</th>
                  <th style={{ textAlign: 'right' }}>Gross Margin</th>
                  <th>Successor SKU</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((p) => {
                  const margin = p.retail_price - p.cost_price;
                  const marginPct = (margin / p.retail_price) * 100;

                  return (
                    <tr key={p.id}>
                      <td style={{ fontWeight: 700, color: '#38bdf8' }}>{p.id}</td>
                      <td>
                        <div style={{ fontWeight: 600, color: 'white' }}>{p.model_name}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{p.brand || 'MobiMart'}</div>
                      </td>
                      <td>
                        <span className="badge badge-blue">{p.segment}</span>
                      </td>
                      <td>{getLifecycleBadge(p.lifecycle_stage)}</td>
                      <td style={{ textAlign: 'right' }}>₹{p.cost_price.toLocaleString('en-IN')}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>₹{p.retail_price.toLocaleString('en-IN')}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600, color: '#34d399' }}>
                        ₹{margin.toLocaleString('en-IN')} ({marginPct.toFixed(0)}%)
                      </td>
                      <td>{p.successor_product_id ? <span style={{ color: '#fbbf24', fontWeight: 600 }}>{p.successor_product_id}</span> : <span style={{ color: '#64748b' }}>None</span>}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '6px' }}>
                          <button
                            onClick={() => setSelectedProduct(p)}
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                          >
                            <Eye size={14} /> Detail
                          </button>
                          <button
                            onClick={() => {
                              setForecastProductSku(p.id);
                              setShowForecastModal(true);
                            }}
                            className="btn btn-primary"
                            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                          >
                            <TrendingUp size={14} /> Forecast
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(10, 14, 23, 0.8)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: '16px' }}>
          <div className="card" style={{ width: '100%', maxWidth: '520px', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <span className="badge badge-blue">{selectedProduct.segment}</span>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white', marginTop: '4px' }}>{selectedProduct.model_name}</h3>
                <span style={{ fontSize: '0.8rem', color: '#38bdf8' }}>{selectedProduct.id}</span>
              </div>
              <button onClick={() => setSelectedProduct(null)} className="btn btn-secondary" style={{ padding: '4px 8px' }}>
                Close
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.875rem', marginBottom: '20px', backgroundColor: '#1e293b', padding: '16px', borderRadius: '8px' }}>
              <div>
                <span style={{ color: '#94a3b8' }}>Cost Price:</span>
                <div style={{ fontWeight: 700, color: 'white' }}>₹{selectedProduct.cost_price.toLocaleString('en-IN')}</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Retail Price:</span>
                <div style={{ fontWeight: 700, color: 'white' }}>₹{selectedProduct.retail_price.toLocaleString('en-IN')}</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Unit Margin:</span>
                <div style={{ fontWeight: 700, color: '#34d399' }}>₹{(selectedProduct.retail_price - selectedProduct.cost_price).toLocaleString('en-IN')}</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Lifecycle Stage:</span>
                <div>{getLifecycleBadge(selectedProduct.lifecycle_stage)}</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Successor SKU:</span>
                <div style={{ fontWeight: 600, color: '#fbbf24' }}>{selectedProduct.successor_product_id || 'None'}</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Rumoured Launch:</span>
                <div style={{ fontWeight: 600, color: selectedProduct.is_rumoured ? '#f43f5e' : '#34d399' }}>
                  {selectedProduct.is_rumoured ? 'Yes' : 'No'}
                </div>
              </div>
            </div>

            <button
              onClick={() => {
                setForecastProductSku(selectedProduct.id);
                setSelectedProduct(null);
                setShowForecastModal(true);
              }}
              className="btn btn-primary"
              style={{ width: '100%' }}
            >
              <Cpu size={16} /> Run Demand Forecast for {selectedProduct.id}
            </button>
          </div>
        </div>
      )}

      {/* Forecast Modal */}
      {showForecastModal && (
        <ForecastModal
          initialProductId={forecastProductSku || 'PROD_001'}
          planningWeek={planningWeek}
          onClose={() => setShowForecastModal(false)}
        />
      )}
    </div>
  );
};
