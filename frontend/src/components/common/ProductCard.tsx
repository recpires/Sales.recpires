import React, { useState } from 'react';
import { Card, Button, Select, Tag } from 'antd';
import { ShoppingCartOutlined, DeleteOutlined } from '@ant-design/icons';
import { Product } from '../../types/product';

const { Option } = Select;

interface ProductCardProps {
  product: Product;
  onAddToCart: (data: {
    product: Product;
    variantId?: number | null;
    quantity?: number;
    variantSnapshot?: any | null;
  }) => void;
  onDelete: (product: Product) => void;
  isAdmin: boolean;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onAddToCart,
  onDelete,
  isAdmin,
}) => {
  const [selectedVariant, setSelectedVariant] = useState<any>(null);

  const hasVariants = Array.isArray(product.variants) && product.variants.length > 0;
  const displayPrice = selectedVariant?.price ?? product.price ?? 0;
  const displayStock = selectedVariant?.stock ?? product.stock ?? 0;
  const isOutOfStock = displayStock <= 0;

  const handleAddToCart = () => {
    const variantId = selectedVariant?.id ?? null;
    const variantSnapshot = selectedVariant ? { ...selectedVariant } : null;
    onAddToCart({ product, variantId, quantity: 1, variantSnapshot });
  };

  const handleVariantChange = (value: number) => {
    const variant = product.variants?.find((v: any) => v.id === value);
    setSelectedVariant(variant || null);
  };

  return (
    <Card
      hoverable
      className="h-full flex flex-col"
      cover={
        <div className="relative h-48 overflow-hidden">
          <img
            alt={product.name}
            src={product.image || 'https://via.placeholder.com/300x200?text=Sem+Imagem'}
            className="h-full w-full object-cover transition-transform hover:scale-110"
          />
          {isOutOfStock && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <Tag color="red" className="text-lg font-bold">
                ESGOTADO
              </Tag>
            </div>
          )}
          {!isOutOfStock && displayStock < 10 && (
            <Tag color="orange" className="absolute top-2 right-2">
              Últimas unidades
            </Tag>
          )}
        </div>
      }
    >
      <div className="flex flex-col flex-1">
        <h3 className="text-lg font-semibold mb-2 line-clamp-2">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2 flex-1">
          {product.description || 'Sem descrição'}
        </p>

        {hasVariants && (
          <div className="mb-3">
            <Select
              placeholder="Selecione uma opção"
              style={{ width: '100%' }}
              onChange={handleVariantChange}
              value={selectedVariant?.id}
            >
              {product.variants?.map((variant: any) => (
                <Option key={variant.id} value={variant.id} disabled={variant.stock <= 0}>
                  {variant.name} - R$ {variant.price.toFixed(2)}
                  {variant.stock <= 0 ? ' (Esgotado)' : ` (${variant.stock} un.)`}
                </Option>
              ))}
            </Select>
          </div>
        )}

        <div className="flex justify-between items-center mb-3">
          <span className="text-2xl font-bold text-green-600">R$ {displayPrice.toFixed(2)}</span>
          <span
            className={`text-sm font-medium ${
              displayStock > 10 ? 'text-gray-500' : 'text-orange-500'
            }`}
          >
            Estoque: {displayStock}
          </span>
        </div>

        <div className="text-xs text-gray-400 mb-3">
          SKU: {selectedVariant?.sku || product.sku}
        </div>

        <div className="flex gap-2 mt-auto">
          <Button
            type="primary"
            icon={<ShoppingCartOutlined />}
            onClick={handleAddToCart}
            disabled={isOutOfStock || (hasVariants && !selectedVariant)}
            block
            size="large"
          >
            {isOutOfStock
              ? 'Esgotado'
              : hasVariants && !selectedVariant
              ? 'Selecione uma opção'
              : 'Adicionar'}
          </Button>
          {isAdmin && (
            <Button danger icon={<DeleteOutlined />} onClick={() => onDelete(product)} size="large">
              Excluir
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default ProductCard;
