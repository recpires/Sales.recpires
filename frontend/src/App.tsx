import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { App as AntApp } from "antd";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import HomePage from "./pages/HomePage";
import SalesPage from "./pages/SalesPage";
import ClientsPage from "./pages/ClientsPage";
import ReportsPage from "./pages/ReportsPage";
import SettingsPage from "./pages/SettingsPage";
import CheckoutPage from "./pages/CheckoutPage";
import CartPage from "./pages/CartPage";
import OrderHistoryPage from "./pages/OrderHistoryPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import WishlistPage from "./pages/WishlistPage";
import authService from "./services/authService";
import { CartProvider } from "./context/CartContext";

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
    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("auth-change", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("auth-change", handleStorageChange);
    };
  }, []);

  const handleLogin = (_email: string, _password: string) => {
    setIsLoggedIn(true);
  };

  return (
    <AntApp>
      <CartProvider>
        <BrowserRouter>
          <Routes>
            <Route
              path="/"
              element={
                isLoggedIn ? (
                  <Navigate to="/home" />
                ) : (
                  <LoginPage onLogin={handleLogin} />
                )
              }
            />
            <Route
              path="/login"
              element={
                isLoggedIn ? (
                  <Navigate to="/home" />
                ) : (
                  <LoginPage onLogin={handleLogin} />
                )
              }
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
              path="/cart"
              element={isLoggedIn ? <CartPage /> : <Navigate to="/" />}
            />
            <Route
              path="/checkout"
              element={isLoggedIn ? <CheckoutPage /> : <Navigate to="/" />}
            />
            <Route
              path="/orders"
              element={isLoggedIn ? <OrderHistoryPage /> : <Navigate to="/" />}
            />
            <Route
              path="/product/:id"
              element={isLoggedIn ? <ProductDetailPage /> : <Navigate to="/" />}
            />
            <Route
              path="/wishlist"
              element={isLoggedIn ? <WishlistPage /> : <Navigate to="/" />}
            />
          </Routes>
        </BrowserRouter>
      </CartProvider>
    </AntApp>
  );
}

export default App;
