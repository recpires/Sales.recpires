import { useState } from 'react';
import { Alert, Spin, Empty } from 'antd';
import { NavBar } from '../components/navbar';
import { Aside } from '../components/aside';
import authService from '../services/authService';
import { useProducts } from '../hooks/useProducts';
import { ProductCard } from '../components/common/ProductCard';
import { Product } from '../types/product';

const HomePage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);

  const { data, isLoading, error } = useProducts();
  const products = data?.results || [];

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  const handleAddToCart = (product: Product) => {
    console.log('Add to cart:', product);
    // TODO: Implementar lógica de carrinho
  };

  const isAdmin = user?.is_staff || user?.is_superuser;

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="flex">
        {isAdmin && <Aside isOpen={isAsideOpen} onToggle={toggleAside} />}

        <main className="flex-1 p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Olá, {user?.first_name || user?.username || 'User'}!
            </h1>
            <p className="text-gray-600">
              Veja todos os produtos disponíveis
            </p>
          </div>

          {/* Lista de produtos */}
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <Spin size="large" />
            </div>
          ) : error ? (
            <Alert
              message="Erro ao carregar produtos"
              description={error instanceof Error ? error.message : 'Ocorreu um erro inesperado'}
              type="error"
              showIcon
            />
          ) : products.length === 0 ? (
            <Empty
              description="Nenhum produto encontrado"
              className="bg-white rounded-lg shadow-md p-8"
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onAddToCart={handleAddToCart}
                />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default HomePage;
