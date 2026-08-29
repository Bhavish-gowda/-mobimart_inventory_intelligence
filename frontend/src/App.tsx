import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import { Layout } from './components/Layout/Layout';
import { OverviewPage } from './pages/OverviewPage';
import { InventoryPage } from './pages/InventoryPage';
import { StoresPage } from './pages/StoresPage';
import { ProductsPage } from './pages/ProductsPage';
import { AllocationPage } from './pages/AllocationPage';
import { EolPage } from './pages/EolPage';
import { SimulationPage } from './pages/SimulationPage';
import { BenchmarkPage } from './pages/BenchmarkPage';

export const App: React.FC = () => {
  const [currentPath, setCurrentPath] = useState(window.location.pathname || '/');
  const [planningWeek, setPlanningWeek] = useState(24);
  const [apiConnected, setApiConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  const checkApiHealth = async () => {
    setLoading(true);
    try {
      const res = await api.getHealth();
      setApiConnected(res.status === 'ok');
    } catch {
      setApiConnected(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkApiHealth();

    const handlePopState = () => {
      setCurrentPath(window.location.pathname || '/');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigateTo = (path: string) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  const getPageTitle = (path: string) => {
    switch (path) {
      case '/':
        return 'Executive Operations Overview';
      case '/inventory':
        return 'Store Inventory Positions';
      case '/stores':
        return 'Karnataka Store Network';
      case '/products':
        return 'Smartphone Catalog SKUs';
      case '/allocation':
        return 'Allocation Control Center';
      case '/eol':
        return 'EOL Risk & Portfolio Transfers';
      case '/simulation':
        return '52-Week Strategy Simulator';
      case '/benchmark':
        return 'Strategy Benchmark Comparison';
      default:
        return 'Executive Operations Overview';
    }
  };

  const renderCurrentPage = () => {
    switch (currentPath) {
      case '/':
        return <OverviewPage planningWeek={planningWeek} onNavigate={navigateTo} />;
      case '/inventory':
        return <InventoryPage />;
      case '/stores':
        return <StoresPage />;
      case '/products':
        return <ProductsPage planningWeek={planningWeek} />;
      case '/allocation':
        return <AllocationPage planningWeek={planningWeek} />;
      case '/eol':
        return <EolPage planningWeek={planningWeek} />;
      case '/simulation':
        return <SimulationPage />;
      case '/benchmark':
        return <BenchmarkPage />;
      default:
        return <OverviewPage planningWeek={planningWeek} onNavigate={navigateTo} />;
    }
  };

  return (
    <Layout
      currentPath={currentPath}
      onNavigate={navigateTo}
      title={getPageTitle(currentPath)}
      planningWeek={planningWeek}
      onWeekChange={setPlanningWeek}
      onRefresh={checkApiHealth}
      apiConnected={apiConnected}
      loading={loading}
    >
      {renderCurrentPage()}
    </Layout>
  );
};

export default App;
