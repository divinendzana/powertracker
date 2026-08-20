import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginAdminPage from './pages/LoginAdminPage';
import LoginEmployePage from './pages/LoginEmployePage';
import DashboardPage from './pages/DashboardPage';
import OperationsPage from './pages/OperationsPage';
import HistoriquePage from './pages/HistoriquePage';
import ParametresPage from './pages/ParametresPage';

function ProtectedRoute({ children, requireAdmin = false }: { children: JSX.Element; requireAdmin?: boolean }) {
  const { user, isAdmin } = useAuth();

  if (!user) {
    return <Navigate to={requireAdmin ? '/login-admin' : '/login-employe'} replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/operations" replace />;
  }

  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to={user.role === 'administratrice' ? '/dashboard' : '/operations'} replace /> : <Navigate to="/login-admin" replace />} />
      <Route path="/login-admin" element={<LoginAdminPage />} />
      <Route path="/login-employe" element={<LoginEmployePage />} />
      <Route path="/dashboard" element={
        <ProtectedRoute requireAdmin>
          <DashboardPage />
        </ProtectedRoute>
      } />
      <Route path="/operations" element={
        <ProtectedRoute requireAdmin={false}>
          <OperationsPage />
        </ProtectedRoute>
      } />
      <Route path="/historique" element={
        <ProtectedRoute requireAdmin>
          <HistoriquePage />
        </ProtectedRoute>
      } />
      <Route path="/parametres" element={
        <ProtectedRoute requireAdmin>
          <ParametresPage />
        </ProtectedRoute>
      } />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;