import React, { useEffect, useState } from 'react';
import { Store as StoreIcon, MapPin, Building2, Users } from 'lucide-react';
import { api } from '../api/client';
import type { Store } from '../types';
import { KpiCard } from '../components/Common/KpiCard';
import { LoadingState } from '../components/Common/LoadingState';
import { ErrorState } from '../components/Common/ErrorState';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const StoresPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stores, setStores] = useState<Store[]>([]);
  const [cityFilter, setCityFilter] = useState('');
  const [locationTypeFilter, setLocationTypeFilter] = useState('');
  const [selectedStore, setSelectedStore] = useState<Store | null>(null);

  const fetchStores = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getStores(cityFilter || undefined, locationTypeFilter || undefined);
      setStores(res.stores);
      if (res.stores.length > 0) setSelectedStore(res.stores[0]);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch stores data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStores();
  }, [cityFilter, locationTypeFilter]);

  // Derive city distribution data for chart
  const cityCounts: Record<string, number> = {};
  stores.forEach((s) => {
    cityCounts[s.city] = (cityCounts[s.city] || 0) + 1;
  });

  const cityChartData = Object.entries(cityCounts).map(([city, count]) => ({
    city,
    stores: count,
  }));

  const totalFootfall = stores.reduce((acc, s) => acc + (s.monthly_footfall || 0), 0);

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className="badge badge-blue">Non-Interchangeable Profiling</span>
          <span className="badge badge-green">25 Outlets</span>
        </div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em', margin: 0 }}>
          Karnataka Store Network Intelligence
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '4px', margin: 0 }}>
          Distinct store profiles across High Street, Premium Malls, Mass Market & Tier-2/Tier-3 Regional Hubs
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid-kpi">
        <KpiCard title="Active Outlets" value={stores.length} subtext="Karnataka State Network" icon={StoreIcon} iconColor="#38bdf8" />
        <KpiCard title="Cities Covered" value={Object.keys(cityCounts).length} subtext="Bangalore, Mysore, Hubli, Mangalore…" icon={MapPin} iconColor="#34d399" />
        <KpiCard title="Monthly Footfall" value={`${(totalFootfall / 100000).toFixed(2)} Lakhs`} subtext="Combined Chain Traffic" icon={Users} iconColor="#fbbf24" />
        <KpiCard title="Avg Outlet Format" value="3,250 sqft" subtext="High-Street & Mall formats" icon={Building2} iconColor="#a855f7" />
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          <div>
            <label style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Filter by City</label>
            <select value={cityFilter} onChange={(e) => setCityFilter(e.target.value)} className="input-select" style={{ width: '100%' }}>
              <option value="">All Cities</option>
              <option value="Bangalore">Bangalore</option>
              <option value="Mysore">Mysore</option>
              <option value="Hubli">Hubli</option>
              <option value="Mangalore">Mangalore</option>
              <option value="Belgaum">Belgaum</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Location Format</label>
            <select value={locationTypeFilter} onChange={(e) => setLocationTypeFilter(e.target.value)} className="input-select" style={{ width: '100%' }}>
              <option value="">All Formats</option>
              <option value="High Street">High Street</option>
              <option value="Premium Mall">Premium Mall</option>
              <option value="Mass Market">Mass Market</option>
              <option value="Tier-2 Center">Tier-2 Center</option>
            </select>
          </div>
        </div>
      </div>

      {/* Selected Store Detailed Profile Card */}
      {selectedStore && (
        <div className="card" style={{ marginBottom: '24px', backgroundColor: '#0f172a', borderLeft: '4px solid #38bdf8' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span className="badge badge-blue">{selectedStore.id}</span>
                <span className="badge badge-green">{selectedStore.location_type}</span>
                <span className="badge badge-amber">{selectedStore.city}</span>
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white', margin: 0 }}>
                {selectedStore.name} ({selectedStore.city})
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px', margin: 0 }}>
                Format: {selectedStore.location_type} • Monthly Footfall: {selectedStore.monthly_footfall?.toLocaleString('en-IN')}
              </p>
            </div>

            <div style={{ display: 'flex', gap: '16px', fontSize: '0.85rem' }}>
              <div>
                <span style={{ color: '#94a3b8' }}>Income Index:</span>
                <div style={{ fontWeight: 700, color: '#34d399', fontSize: '1.1rem' }}>
                  {selectedStore.income_index ? selectedStore.income_index.toFixed(2) : '1.20'}
                </div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Flagship Affinity:</span>
                <div style={{ fontWeight: 700, color: '#38bdf8', fontSize: '1.1rem' }}>
                  {selectedStore.flagship_affinity ? selectedStore.flagship_affinity.toFixed(2) : '1.00'}x
                </div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Budget Affinity:</span>
                <div style={{ fontWeight: 700, color: '#a855f7', fontSize: '1.1rem' }}>
                  {selectedStore.budget_affinity ? selectedStore.budget_affinity.toFixed(2) : '1.00'}x
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Grid with Chart and Table */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px', marginBottom: '24px' }}>
        {/* City Chart */}
        <div className="card">
          <div className="card-title">Store Count by City</div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cityChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="city" type="category" stroke="#94a3b8" width={90} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: 'white' }} />
                <Bar dataKey="stores" fill="#38bdf8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Store Table */}
        {loading ? (
          <LoadingState message="Loading store intelligence profiles…" />
        ) : error ? (
          <ErrorState message={error} onRetry={fetchStores} />
        ) : (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Store ID</th>
                    <th>Store Name</th>
                    <th>City</th>
                    <th>Location Format</th>
                    <th style={{ textAlign: 'right' }}>Size (sqft)</th>
                    <th style={{ textAlign: 'right' }}>Monthly Footfall</th>
                    <th style={{ textAlign: 'right' }}>Income Index</th>
                  </tr>
                </thead>
                <tbody>
                  {stores.map((s) => (
                    <tr
                      key={s.id}
                      onClick={() => setSelectedStore(s)}
                      style={{
                        cursor: 'pointer',
                        backgroundColor: selectedStore?.id === s.id ? 'rgba(56, 189, 248, 0.08)' : undefined,
                      }}
                    >
                      <td style={{ fontWeight: 700, color: '#38bdf8' }}>{s.id}</td>
                      <td style={{ fontWeight: 600, color: 'white' }}>{s.name}</td>
                      <td>{s.city}</td>
                      <td>
                        <span className="badge badge-blue">{s.location_type}</span>
                      </td>
                      <td style={{ textAlign: 'right' }}>{s.store_size_sqft?.toLocaleString('en-IN') || '-'}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{s.monthly_footfall?.toLocaleString('en-IN') || '-'}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600, color: '#34d399' }}>
                        {s.income_index ? s.income_index.toFixed(2) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
