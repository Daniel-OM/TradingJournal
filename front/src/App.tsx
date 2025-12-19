import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Layout from './components/Layout';
import {
  HomePage,
  LoginPage,
  RegisterPage,
  TradesPage,
  TradeDetailPage,
  TradeFormPage,
  StrategiesPage,
  WatchlistsPage,
  PerformancePage,
  TestLoginPage,
  AssetsPage,
  SettingsPage,
} from './pages';

const App: React.FC = () => {
  const { checkAuth, isAuthenticated } = useAuthStore();
  const [isInitializing, setIsInitializing] = React.useState(true);

  React.useEffect(() => {
    // Verificar autenticación al cargar la app
    checkAuth().finally(() => {
      setIsInitializing(false);
    });
  }, [checkAuth]);

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <Router>
      {isAuthenticated ? (
        // Rutas protegidas con Layout (Navbar + Sidebar)
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/trades" element={<TradesPage />} />
            <Route path="/trades/new" element={<TradeFormPage />} />
            <Route path="/trades/:id" element={<TradeDetailPage />} />
            <Route path="/trades/:id/edit" element={<TradeFormPage />} />
            <Route path="/strategies" element={<StrategiesPage />} />
            <Route path="/watchlists" element={<WatchlistsPage />} />
            <Route path="/performance" element={<PerformancePage />} />
            <Route path="/assets" element={<AssetsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      ) : (
        // Rutas públicas sin Layout
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/test-login" element={<TestLoginPage />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </Router>
  );
};

export default App;

