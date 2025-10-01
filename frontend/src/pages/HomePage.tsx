import { useState, useEffect } from 'react';
import { NavBar } from '../components/navbar';
import { Aside } from '../components/aside';
import authService from '../services/authService';
import productService, { Product } from '../services/productService';

const HomePage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await productService.getProducts();
      setProducts(response.results);
    } catch (err) {
      console.error('Error loading products:', err);
      setError('Erro ao carregar produtos');
    } finally {
      setLoading(false);
    }
  };

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="flex">
        <Aside isOpen={isAsideOpen} onToggle={toggleAside} />

        <main className="flex-1 p-8">
          {/* Botão de toggle do aside */}
          <button
            onClick={toggleAside}
            className="mb-4 lg:hidden flex items-center space-x-2 px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <span>Menu</span>
          </button>
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
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          ) : products.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Nenhum produto encontrado</h3>
              <p className="text-gray-600">Adicione produtos para começar</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map((product) => (
                <div key={product.id} className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden hover:shadow-xl transition-shadow duration-300">
                  {/* Imagem placeholder */}
                  <div className="h-48 bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
                    <svg className="w-20 h-20 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>

                  {/* Informações do produto */}
                  <div className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-bold text-gray-900 truncate flex-1">{product.name}</h3>
                      {product.stock > 0 ? (
                        <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full ml-2">
                          Em estoque
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-full ml-2">
                          Esgotado
                        </span>
                      )}
                    </div>

                    <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description}</p>

                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="text-xs text-gray-500">Categoria</p>
                        <p className="text-sm font-medium text-gray-900">{product.category}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">Estoque</p>
                        <p className="text-sm font-medium text-gray-900">{product.stock} un.</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                      <div>
                        <p className="text-xs text-gray-500">Preço</p>
                        <p className="text-xl font-bold text-orange-600">R$ {parseFloat(product.price).toFixed(2)}</p>
                      </div>
                      <button className="px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-lg transition-all duration-300 shadow-md hover:shadow-lg text-sm font-medium">
                        Ver detalhes
                      </button>
                    </div>

                    <div className="mt-2">
                      <p className="text-xs text-gray-400">SKU: {product.sku}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default HomePage;
