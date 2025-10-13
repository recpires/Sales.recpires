import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { App as AntApp } from 'antd';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import SalesPage from './pages/SalesPage';
import ClientsPage from './pages/ClientsPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';
import CheckoutPage from './pages/CheckoutPage';
import authService from './services/authService';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(authService.isAuthenticated());

  useEffect(() => {
    // Verifica se o usuário está autenticado ao carregar o app
    setIsLoggedIn(authService.isAuthenticated());

    // Listener para mudanças no localStorage (logout)
    const handleStorageChange = () => {
      setIsLoggedIn(authService.isAuthenticated());
    };

    // Listener customizado para mudanças de autenticação
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth-change', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-change', handleStorageChange);
    };
  }, []);

  const handleLogin = (email: string, password: string) => {
    console.log('Login attempt:', { email, password });
    setIsLoggedIn(true);
  };

  return (
    <AntApp>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={isLoggedIn ? <Navigate to="/home" /> : <LoginPage onLogin={handleLogin} />}
          />
          <Route
            path="/login"
            element={isLoggedIn ? <Navigate to="/home" /> : <LoginPage onLogin={handleLogin} />}
          />
          <Route
            path="/register"
            element={isLoggedIn ? <Navigate to="/home" /> : <RegisterPage />}
          />
          <Route
            path="/home"
            element={isLoggedIn ? <HomePage /> : <Navigate to="/" />}
          />
          <Route
            path="/sales"
            element={isLoggedIn ? <SalesPage /> : <Navigate to="/" />}
          />
          <Route
            path="/clients"
            element={isLoggedIn ? <ClientsPage /> : <Navigate to="/" />}
          />
          <Route
            path="/reports"
            element={isLoggedIn ? <ReportsPage /> : <Navigate to="/" />}
          />
          <Route
            path="/settings"
            element={isLoggedIn ? <SettingsPage /> : <Navigate to="/" />}
          />
          <Route
            path="/checkout"
            element={isLoggedIn ? <CheckoutPage /> : <Navigate to="/" />}
          />
        </Routes>
      </BrowserRouter>
    </AntApp>
  );
}

export default App;
