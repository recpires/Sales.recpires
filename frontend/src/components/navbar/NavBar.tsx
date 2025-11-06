import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { ShoppingCart, Heart, User, LogOut, Package, Users, Settings, BarChart, ArrowDownUp } from 'lucide-react'; // CORREÇÃO 1: Importação de lucide-react (presumo que esteja instalado)
import useAuth from '../../hooks/useAuth'; // CORREÇÃO 2: Importação de useAuth (presume-se export default)
import { useStore } from '../../hooks/useStore'; // CORREÇÃO 3: Importação de useStore
import { useCart } from '../../context/CartContext';
import { Button } from '../common/Button'; // CORREÇÃO 7: Importação de Button (diretamente)
import { useTranslation } from 'react-i18next'; // CORREÇÃO: Adicionada importação faltante de useTranslation

const NavBar: React.FC = () => {
  const { t } = useTranslation();
  const { isAuthenticated, user, logout } = useAuth();
  const { store } = useStore();
  const { state } = useCart(); // CORREÇÃO 4: Uso correto do CartContext para acessar o estado
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Checa se o usuário logado é o proprietário da loja atual
  const isStoreOwner = store && user && user.id === store.user.id;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // CORREÇÃO 5: Tipagem explícita para os parâmetros da função reduce
  const cartItemCount = state.cartItems.reduce((total: number, item: { quantity: number }) => total + item.quantity, 0);

  // Links de Navegação Comuns
  const navLinks = [
    { to: '/', icon: <Package size={18} />, label: t('Produtos') },
    // A rota de Vendas agora foca em vendas/pedidos já realizados
    { to: '/sales', icon: <ArrowDownUp size={18} />, label: t('Pedidos de Venda'), ownerOnly: true }, 
    { to: '/purchase-orders', icon: <Package size={18} />, label: t('Pedidos de Compra (PO)'), ownerOnly: true }, // Novo Link
    { to: '/clients', icon: <Users size={18} />, label: t('Clientes'), ownerOnly: true },
    { to: '/reports', icon: <BarChart size={18} />, label: t('Relatórios'), ownerOnly: true },
  ];

  return (
    <header className="bg-white shadow-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo/Título da Loja */}
          <NavLink to="/" className="text-xl font-bold text-indigo-600 hover:text-indigo-700 transition duration-150">
            {store ? store.name : t('E-Commerce App')}
          </NavLink>

          {/* Links de Navegação (Desktop) */}
          <nav className="hidden md:flex space-x-4 items-center">
            {navLinks.map((link) => {
              if (link.ownerOnly && !isStoreOwner) {
                return null;
              }
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) => 
                    `flex items-center space-x-1 px-3 py-2 text-sm font-medium rounded-md transition duration-150 ${
                      isActive 
                        ? 'bg-indigo-50 text-indigo-700' 
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  {link.icon}
                  <span>{link.label}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Ícones de Ação (Carrinho, Lista de Desejos, Usuário) */}
          <div className="flex items-center space-x-4">
            
            {/* Carrinho */}
            <NavLink to="/cart" className="relative p-2 rounded-full text-gray-500 hover:text-indigo-600 hover:bg-gray-100 transition duration-150">
              <ShoppingCart size={20} />
              {cartItemCount > 0 && (
                <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                  {cartItemCount}
                </span>
              )}
            </NavLink>

            {/* Lista de Desejos */}
            {isAuthenticated && (
              <NavLink to="/wishlist" className="p-2 rounded-full text-gray-500 hover:text-indigo-600 hover:bg-gray-100 transition duration-150">
                <Heart size={20} />
              </NavLink>
            )}

            {/* Menu do Usuário */}
            <div className="relative">
              {/* CORREÇÃO 6: Uso do tipo 'variant' do botão */}
              <Button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2 bg-transparent text-gray-500 hover:text-indigo-600 hover:bg-gray-100 transition duration-150 border-none">
                <User size={20} />
              </Button>
              
              {isMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-xl py-1 z-50 border border-gray-100">
                  {!isAuthenticated ? (
                    <>
                      <NavLink to="/login" className="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700" onClick={() => setIsMenuOpen(false)}>
                        {t('Entrar')}
                      </NavLink>
                      <NavLink to="/register" className="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700" onClick={() => setIsMenuOpen(false)}>
                        {t('Registrar')}
                      </NavLink>
                    </>
                  ) : (
                    <>
                      <span className="block px-4 py-2 text-sm text-gray-900 truncate">{user?.username || t('Usuário')}</span>
                      <div className="border-t border-gray-100 my-1"></div>
                      <NavLink to="/orders" className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700" onClick={() => setIsMenuOpen(false)}>
                        <ArrowDownUp size={16} /><span>{t('Meus Pedidos')}</span>
                      </NavLink>
                      {isStoreOwner && (
                        <NavLink to="/settings" className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700" onClick={() => setIsMenuOpen(false)}>
                          <Settings size={16} /><span>{t('Configurações da Loja')}</span>
                        </NavLink>
                      )}
                      <button onClick={handleLogout} className="flex items-center space-x-2 w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50" >
                        <LogOut size={16} /><span>{t('Sair')}</span>
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Menu Hamburger (Mobile) */}
            <button
                className="md:hidden p-2 rounded-full text-gray-500 hover:text-indigo-600 hover:bg-gray-100 transition duration-150"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
                {/* Ícone de Menu */}
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
            </button>
          </div>
        </div>
        
        {/* Menu de Navegação (Mobile - Visível quando isMenuOpen) */}
        {/* Obs: O menu lateral de gestão é tratado no componente Aside */}
        
      </div>
    </header>
  );
};

export default NavBar;