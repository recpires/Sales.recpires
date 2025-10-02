import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
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
      </Routes>
    </BrowserRouter>
  );
}

export default App;
