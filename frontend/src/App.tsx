import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Layout } from "./components/layout/Layout"; // CORREÇÃO 1: Caminho de importação
import HomePage from "./pages/HomePage";
import ProductDetailPage from "./pages/ProductDetailPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import OrderHistoryPage from "./pages/OrderHistoryPage";
import WishlistPage from "./pages/WishlistPage";
import SettingsPage from "./pages/SettingsPage";
import SalesPage from "./pages/SalesPage";
import ClientsPage from "./pages/ClientsPage";
import ReportsPage from "./pages/ReportsPage";

// Novo componente para Pedido de Ordem
import PurchaseOrderPage from "./pages/PurchaseOrderPage";

import { CartProvider } from "./context/CartContext";
import { useStore } from "./hooks/useStore"; // CORREÇÃO 2: Importação de useStore
import useAuth from "./hooks/useAuth"; // CORREÇÃO 3: Importação de useAuth (presume-se export default)
import { StoreSetupModal } from "./components/common/StoreSetupModal"; // CORREÇÃO 4: Importação de StoreSetupModal (diretamente)

const ProtectedRoute = ({
  children,
  isAdminOnly = false,
}: {
  children: JSX.Element;
  isAdminOnly?: boolean;
}) => {
  const { isAuthenticated, user, loading } = useAuth();
  const { store } = useStore();

  // Se estiver carregando, mostra um loader simples
  if (loading)
    return (
      <div className="flex justify-center items-center h-screen">
        Carregando...
      </div>
    );

  // Verifica autenticação
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // Verifica se o usuário é o dono da loja para páginas de gestão
  const isOwner = store && user.id === store.user.id;

  if (isAdminOnly && !isOwner) {
    // Redireciona usuários não-proprietários para a home
    return <Navigate to="/" replace />;
  }

  return children;
};

const App: React.FC = () => {
  const { i18n } = useTranslation();
  const { store, loading: storeLoading, error: storeError } = useStore();
  const { isAuthenticated, user } = useAuth();

  // Variável 'isStoreOwner' removida, pois não era utilizada.

  // Estado para controlar a exibição do modal de configuração inicial
  const [showSetupModal, setShowSetupModal] = React.useState(false);

  useEffect(() => {
    // Lógica para mostrar o modal de configuração da loja
    if (isAuthenticated && user && !storeLoading && !store && !storeError) {
      // Se autenticado, mas sem loja, assume que precisa configurar.
      setShowSetupModal(true);
    } else {
      setShowSetupModal(false);
    }
  }, [isAuthenticated, user, store, storeLoading, storeError]);

  // Defina o idioma inicial
  useEffect(() => {
    const savedLanguage = localStorage.getItem("language") || "pt-BR";
    i18n.changeLanguage(savedLanguage);
  }, [i18n]);

  return (
    <Router>
      <CartProvider>
        <Layout>
          {showSetupModal && (
            <StoreSetupModal onClose={() => setShowSetupModal(false)} />
          )}
          <Routes>
            {/* Rotas de Cliente (Públicas/Autenticadas) */}
            <Route path="/" element={<HomePage />} />
            <Route path="/product/:id" element={<ProductDetailPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route
              path="/checkout"
              element={
                <ProtectedRoute>
                  <CheckoutPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/orders"
              element={
                <ProtectedRoute>
                  <OrderHistoryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/wishlist"
              element={
                <ProtectedRoute>
                  <WishlistPage />
                </ProtectedRoute>
              }
            />

            {/* Rotas de Autenticação */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Rotas de Administrador/Gestão da Loja (Protegidas) */}
            <Route
              path="/settings"
              element={
                <ProtectedRoute isAdminOnly={true}>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/sales"
              element={
                <ProtectedRoute isAdminOnly={true}>
                  <SalesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/clients"
              element={
                <ProtectedRoute isAdminOnly={true}>
                  <ClientsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute isAdminOnly={true}>
                  <ReportsPage />
                </ProtectedRoute>
              }
            />

            {/* NOVA ROTA: Pedidos de Compra (PO) */}
            <Route
              path="/purchase-orders"
              element={
                <ProtectedRoute isAdminOnly={true}>
                  <PurchaseOrderPage />
                </ProtectedRoute>
              }
            />

            {/* Redirecionamento 404 para a Home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </CartProvider>
    </Router>
  );
};

export default App;
