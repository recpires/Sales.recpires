import { FC } from 'react';
import { Card, Tag, Typography } from 'antd';
import { ShoppingCartOutlined } from '@ant-design/icons';
import { Product } from '../../types/product';

const { Text, Title } = Typography;

interface ProductCardProps {
  product: Product;
  onAddToCart?: (product: Product) => void;
}

const colorMap: Record<string, string> = {
  red: '#f5222d',
  blue: '#1890ff',
  green: '#52c41a',
  black: '#000000',
  white: '#ffffff',
  yellow: '#faad14',
  pink: '#eb2f96',
  purple: '#722ed1',
  orange: '#fa8c16',
  gray: '#8c8c8c',
};

export const ProductCard: FC<ProductCardProps> = ({ product, onAddToCart }) => {
  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(product);
    }
  };

  return (
    <Card
      hoverable
      className="h-full flex flex-col"
      cover={
        <div className="h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
          <div className="text-6xl text-gray-400">📦</div>
        </div>
      }
      actions={
        product.stock > 0
          ? [
              <div
                key="add-to-cart"
                onClick={handleAddToCart}
                className="flex items-center justify-center gap-2 cursor-pointer hover:text-blue-600 transition-colors"
              >
                <ShoppingCartOutlined />
                <span>Adicionar ao Carrinho</span>
              </div>,
            ]
          : []
      }
    >
      <div className="flex flex-col gap-3">
        <Title level={4} className="!mb-0 line-clamp-2">
          {product.name}
        </Title>

        {product.description && (
          <Text type="secondary" className="line-clamp-2 text-sm">
            {product.description}
          </Text>
        )}

        <div className="flex items-center gap-2 flex-wrap">
          <Tag color={colorMap[product.color] || 'default'} className="flex items-center gap-1">
            <div
              className="w-3 h-3 rounded-full border border-gray-300"
              style={{ backgroundColor: colorMap[product.color] }}
            />
            {product.color_display}
          </Tag>
          <Tag>{product.size_display}</Tag>
        </div>

        <div className="flex items-center justify-between mt-2">
          <div className="flex flex-col">
            <Text className="text-2xl font-bold text-green-600">
              R$ {parseFloat(product.price).toFixed(2)}
            </Text>
            <Text type="secondary" className="text-xs">
              SKU: {product.sku}
            </Text>
          </div>

          <div className="flex flex-col items-end">
            {product.stock > 0 ? (
              <>
                <Tag color="success">Em estoque</Tag>
                <Text type="secondary" className="text-xs">
                  {product.stock} disponíveis
                </Text>
              </>
            ) : (
              <Tag color="error">Esgotado</Tag>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ProductCard;
