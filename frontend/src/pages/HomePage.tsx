import React, { useState, useEffect } from 'react';
import { Button, Input, Alert, Empty, Spin, Modal, message } from 'antd';
import { PlusOutlined, SearchOutlined, ShopOutlined } from '@ant-design/icons';
import NavBar from '../components/navbar/NavBar';
import Aside from '../components/aside/Aside';
import ProductCard from '../components/common/ProductCard';
import ProductForm from '../components/common/ProductForm';
import ConfirmDeleteModal from '../components/common/ConfirmDeleteModal';
import { StoreSetupModal } from '../components/common/StoreSetupModal';
import { useCart } from '../context/CartContext';
import authService from '../services/authService';
import { useProducts, useCreateProductWithImage, useDeleteProduct } from '../hooks/useProducts';
import { useMyStore } from '../hooks/useStore';
import { Product } from '../types/product';

const HomePage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isStoreSetupModalOpen, setIsStoreSetupModalOpen] = useState(false);
  const [productToDelete, setProductToDelete] = useState<Product | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const { data, isLoading, error } = useProducts();
  const { data: myStore, isLoading: isLoadingStore, error: storeError } = useMyStore();
  const allProducts = data?.results || [];

  const isAdmin = user?.is_staff || user?.is_superuser;
  const hasStore = !!myStore;

  // Auto-open store setup modal if admin doesn't have a store
  useEffect(() => {
    const err = storeError as any;
    const isNotFound = err?.response?.status === 404 || err?.status === 404;
    if (isAdmin && !isLoadingStore && !hasStore && isNotFound) {
      setIsStoreSetupModalOpen(true);
    }
  }, [isAdmin, isLoadingStore, hasStore, storeError]);

  // Filtra produtos baseado no termo de pesquisa
  const filteredProducts = allProducts.filter((product) => {
    const q = searchTerm.toLowerCase();
    if (!q) return true;
    const matchesName = product.name.toLowerCase().includes(q);
    const matchesDesc = product.description?.toLowerCase().includes(q);
    const matchesSku = (product.sku ?? '').toLowerCase().includes(q);
    const matchesVariantSku =
      Array.isArray(product.variants) &&
      product.variants.some((v: any) => (v.sku ?? '').toLowerCase().includes(q));
    return matchesName || matchesDesc || matchesSku || matchesVariantSku;
  });

  // Normalize product objects so UI code that expects price/stock continues working
  const normalizedProducts = filteredProducts.map((p: any) => {
    const firstVariant = Array.isArray(p.variants) && p.variants.length > 0 ? p.variants[0] : null;
    return {
      ...p,
      price: p.price ?? firstVariant?.price ?? 0,
      stock: p.stock ?? firstVariant?.stock ?? 0,
    };
  });

  const createProductMutation = useCreateProductWithImage();
  const deleteProductMutation = useDeleteProduct();

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  const { dispatch } = useCart();

  const handleAddToCart = (data: {
    product: Product;
    variantId?: number | null;
    quantity?: number;
    variantSnapshot?: any | null;
  }) => {
    try {
      const product = data.product;
      const variantId = data.variantId ?? null;
      const quantity = data.quantity ?? 1;
      const variantSnapshot = data.variantSnapshot ?? null;

      dispatch({
        type: 'ADD_ITEM',
        payload: { productId: product.id, variantId, quantity, product, variantSnapshot },
      });
      message.success('Produto adicionado ao carrinho');
    } catch (err) {
      message.error('Erro ao adicionar ao carrinho');
    }
  };

  const handleCreateProduct = async (data: any, image?: File) => {
    try {
      await createProductMutation.mutateAsync({ data, image });
      message.success('Produto criado com sucesso!');
      setIsModalOpen(false);
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Erro ao criar produto');
      throw error;
    }
  };

  const handleDeleteProduct = (product: Product) => {
    setProductToDelete(product);
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!productToDelete) return;

    try {
      await deleteProductMutation.mutateAsync(productToDelete.id);
      message.success('Produto excluído com sucesso!');
      setIsDeleteModalOpen(false);
      setProductToDelete(null);
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Erro ao excluir produto');
    }
  };

  const handleCancelDelete = () => {
    setIsDeleteModalOpen(false);
    setProductToDelete(null);
  };

  const handleStoreSetupSuccess = () => {
    message.success('Loja configurada! Agora você pode criar produtos.');
    setIsStoreSetupModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="flex">
        {isAdmin && <Aside isOpen={isAsideOpen} onToggle={toggleAside} />}

        <main className="flex-1 p-8">
          {/* Header */}
          {isAdmin ? (
            <div className="mb-8">
              {/* Store Setup Alert */}
              {!isLoadingStore && !hasStore && (
                <Alert
                  message="Configure sua Loja"
                  description="Você precisa configurar sua loja antes de criar produtos."
                  type="warning"
                  showIcon
                  icon={<ShopOutlined />}
                  action={
                    <Button size="small" type="primary" onClick={() => setIsStoreSetupModalOpen(true)}>
                      Configurar Agora
                    </Button>
                  }
                  className="mb-6"
                />
              )}

              <div className="flex justify-between items-center mb-6">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    Olá, {user?.username || 'Admin'}!
                  </h1>
                  <p className="text-gray-600">Gerencie seus produtos e vendas</p>
                </div>
                {hasStore && (
                  <Button
                    type="primary"
                    size="large"
                    icon={<PlusOutlined />}
                    onClick={() => setIsModalOpen(true)}
                  >
                    Novo Produto
                  </Button>
                )}
              </div>
              <Input
                size="large"
                placeholder="Buscar produtos por nome, descrição ou SKU..."
                prefix={<SearchOutlined className="text-gray-400" />}
                value={searchTerm}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                className="rounded-lg"
                allowClear
              />
            </div>
          ) : (
            <div className="mb-8">
              {/* Banner estilo Shopee */}
              <div className="bg-gradient-to-r from-orange-500 via-red-500 to-pink-500 rounded-lg p-8 mb-6 shadow-lg">
                <h1 className="text-4xl font-bold text-white mb-3">
                  🔥 Ofertas Imperdíveis para Você!
                </h1>
                <p className="text-white text-lg font-medium mb-2">
                  Olá, {user?.username || 'Visitante'}!
                </p>
                <p className="text-white/90">Aproveite os melhores preços e ofertas especiais</p>
              </div>

              {/* Campo de Pesquisa */}
              <div className="mb-6">
                <Input
                  size="large"
                  placeholder="Buscar produtos por nome, descrição ou SKU..."
                  prefix={<SearchOutlined className="text-gray-400" />}
                  value={searchTerm}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                  className="rounded-lg shadow-md"
                  allowClear
                />
              </div>

              {/* Categorias/Tags estilo Shopee */}
              <div className="flex gap-3 overflow-x-auto pb-2 mb-4">
                <div className="bg-white rounded-full px-6 py-2 shadow-sm border-2 border-orange-500 text-orange-500 font-semibold whitespace-nowrap cursor-pointer hover:bg-orange-50 transition-colors">
                  🏷️ Todos os Produtos
                </div>
                <div className="bg-white rounded-full px-6 py-2 shadow-sm border border-gray-200 text-gray-700 font-medium whitespace-nowrap cursor-pointer hover:bg-gray-50 transition-colors">
                  ⚡ Flash Sale
                </div>
                <div className="bg-white rounded-full px-6 py-2 shadow-sm border border-gray-200 text-gray-700 font-medium whitespace-nowrap cursor-pointer hover:bg-gray-50 transition-colors">
                  🎁 Frete Grátis
                </div>
                <div className="bg-white rounded-full px-6 py-2 shadow-sm border border-gray-200 text-gray-700 font-medium whitespace-nowrap cursor-pointer hover:bg-gray-50 transition-colors">
                  🌟 Mais Vendidos
                </div>
                <div className="bg-white rounded-full px-6 py-2 shadow-sm border border-gray-200 text-gray-700 font-medium whitespace-nowrap cursor-pointer hover:bg-gray-50 transition-colors">
                  💎 Novidades
                </div>
              </div>
            </div>
          )}

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
          ) : normalizedProducts.length === 0 ? (
            <Empty
              description="Nenhum produto encontrado"
              className="bg-white rounded-lg shadow-md p-8"
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {normalizedProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onAddToCart={handleAddToCart}
                  onDelete={handleDeleteProduct}
                  isAdmin={isAdmin}
                />
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Modal de Criação de Produto */}
      <Modal
        title="Criar Novo Produto"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={800}
        destroyOnClose
      >
        <ProductForm
          onSubmit={handleCreateProduct}
          submitText="Criar Produto"
          loading={createProductMutation.isPending}
        />
      </Modal>

      {/* Modal de Confirmação de Exclusão */}
      <ConfirmDeleteModal
        isOpen={isDeleteModalOpen}
        productName={productToDelete?.name || ''}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        loading={deleteProductMutation.isPending}
      />

      {/* Modal de Configuração de Loja */}
      <StoreSetupModal
        isOpen={isStoreSetupModalOpen}
        onClose={() => setIsStoreSetupModalOpen(false)}
        onSuccess={handleStoreSetupSuccess}
        store={myStore}
      />
    </div>
  );
};

export default HomePage;
