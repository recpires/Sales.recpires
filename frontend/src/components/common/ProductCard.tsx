import { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, Tag, Typography, Modal, Select, InputNumber, Button } from 'antd';
import { ShoppingCartOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { Product } from '../../types/product';

const { Text, Title } = Typography;

interface ProductCardProps {
  product: Product;
  onAddToCart?: (data: { product: Product; variantId?: number | null; quantity?: number; variantSnapshot?: any | null }) => void;
  onDelete?: (product: Product) => void;
  isAdmin?: boolean;
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

export const ProductCard: FC<ProductCardProps> = ({ product, onAddToCart, onDelete, isAdmin }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState<number | null>(null);
  const [quantity, setQuantity] = useState(1);

  const handleViewDetails = () => {
    navigate(`/product/${product.id}`);
  };

  const handleAddToCart = () => {
    if (product.variants && product.variants.length > 0) {
      setIsModalOpen(true);
      return;
    }

    if (onAddToCart) onAddToCart({ product, variantId: null, quantity: 1, variantSnapshot: null });
  };

  const confirmAdd = () => {
    if (onAddToCart) {
      const variant = product.variants?.find(v => v.id === selectedVariant) ?? null;
      const variantSnapshot = variant ? { id: variant.id, sku: variant.sku, price: variant.price, color: variant.color ?? null, size: variant.size ?? null, image: variant.image ?? null } : null;
      onAddToCart({ product, variantId: selectedVariant, quantity, variantSnapshot });
    }
    setIsModalOpen(false);
    setSelectedVariant(null);
    setQuantity(1);
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete(product);
    }
  };

  const actions = [];

  // Ver detalhes sempre disponível
  actions.push(
    <div
      key="view-details"
      onClick={handleViewDetails}
      className="flex items-center justify-center gap-2 cursor-pointer hover:text-blue-600 transition-colors"
    >
      <EyeOutlined />
      <span>Ver Detalhes</span>
    </div>
  );

  if (!isAdmin && product.stock > 0) {
    actions.push(
        <div
        key="add-to-cart"
        onClick={handleAddToCart}
        className="flex items-center justify-center gap-2 cursor-pointer hover:text-blue-600 transition-colors"
      >
        <ShoppingCartOutlined />
        <span>{t('product.add_to_cart')}</span>
      </div>
    );
  }

  if (isAdmin) {
    actions.push(
        <div
        key="delete"
        onClick={handleDelete}
        className="flex items-center justify-center gap-2 cursor-pointer bg-red-600 text-black hover:text-white transition-colors rounded-full px-4 py-2 shadow-md hover:shadow-lg"
      >
        <DeleteOutlined />
        <span>{t('product.delete')}</span>
      </div>
    );
  }

  // Simula desconto aleatório para usuário comum
  const randomDiscount = !isAdmin && product.stock > 0 ? Math.floor(Math.random() * 50) + 10 : 0;
  const hasDiscount = randomDiscount > 0;
  const originalPrice = hasDiscount ? parseFloat(product.price) * (1 + randomDiscount / 100) : parseFloat(product.price);
  const discountedPrice = parseFloat(product.price);

  return (
    <>
    <Card
      hoverable
      className="h-full flex flex-col relative overflow-hidden"
      cover={
        <div className="relative">
          {product.image ? (
            <img
              src={product.image}
              alt={product.name}
              className="h-48 w-full object-cover"
            />
          ) : (
            <div className="h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
              <div className="text-6xl text-gray-400">📦</div>
            </div>
          )}

          {/* Labels estilo Shopee para usuário comum */}
          {!isAdmin && hasDiscount && (
            <>
              {/* Label de desconto no canto superior esquerdo */}
              <div className="absolute top-0 left-0 bg-gradient-to-r from-red-600 to-orange-500 text-white px-3 py-1 text-sm font-bold shadow-lg">
                -{randomDiscount}%
              </div>

              {/* Badge de frete grátis */}
              {product.stock > 10 && (
                <div className="absolute top-10 left-0 bg-blue-600 text-white px-2 py-0.5 text-xs font-semibold shadow-md">
                  {t('product.free_shipping')}
                </div>
              )}
            </>
          )}

          {/* Label de estoque baixo */}
          {!isAdmin && product.stock > 0 && product.stock <= 5 && (
            <div className="absolute bottom-2 left-2 bg-yellow-500 text-white px-2 py-1 text-xs font-bold rounded shadow-md animate-pulse">
              {t('product.low_stock_warning')}
            </div>
          )}

          {/* Label de novidade */}
          {!isAdmin && product.stock > 15 && (
            <div className="absolute top-0 right-0 bg-purple-600 text-white px-3 py-1 text-xs font-bold shadow-lg rounded-bl-lg">
              {t('product.new')}
            </div>
          )}
        </div>
      }
      actions={actions}
    >
      <div className="flex flex-col gap-3">
        <Title level={4} className="!mb-0 line-clamp-2">
          {product.name}
        </Title>

        {/* Seller information */}
        {product.seller_name && (
          <div className="flex items-center gap-2 py-1 px-2 bg-blue-50 rounded">
            <Text type="secondary" className="text-xs">
              Vendedor: <span className="font-semibold text-blue-600">{product.seller_name}</span>
              {product.store_name && <span className="text-gray-400"> • {product.store_name}</span>}
            </Text>
          </div>
        )}

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
          <div className="flex flex-col flex-1">
            {!isAdmin && hasDiscount ? (
              <>
                <div className="flex items-baseline gap-2">
                  <Text className="text-2xl font-bold text-orange-600">
                    R$ {discountedPrice.toFixed(2)}
                  </Text>
                  <Text delete type="secondary" className="text-sm">
                    R$ {originalPrice.toFixed(2)}
                  </Text>
                </div>
                <div className="flex items-center gap-2 mt-1">
                    <div className="bg-orange-100 text-orange-600 px-2 py-0.5 rounded text-xs font-bold">
                    {t('product.save_amount', { amount: (originalPrice - discountedPrice).toFixed(2) })}
                  </div>
                </div>
                <Text type="secondary" className="text-xs mt-1">
                  {t('product.sku')}: {product.sku}
                </Text>
              </>
            ) : (
              <>
                <Text className="text-2xl font-bold text-green-600">
                  R$ {parseFloat(product.price).toFixed(2)}
                </Text>
                <Text type="secondary" className="text-xs">
                  SKU: {product.sku}
                </Text>
              </>
            )}
          </div>

          <div className="flex flex-col items-end">
            {product.stock > 0 ? (
              <>
                {!isAdmin ? (
                  <>
                    <div className="bg-green-50 text-green-700 px-2 py-1 rounded text-xs font-semibold border border-green-200">
                      ✓ {t('product.available')}
                    </div>
                    <Text type="secondary" className="text-xs mt-1">
                      {product.stock} em estoque
                    </Text>
                  </>
                ) : (
                  <>
                    <Tag color="success">{t('product.in_stock')}</Tag>
                    <Text type="secondary" className="text-xs">
                      {product.stock} disponíveis
                    </Text>
                  </>
                )}
              </>
            ) : (
              <Tag color="error">{t('product.sold_out')}</Tag>
            )}
          </div>
        </div>
      </div>
    </Card>
    <Modal title={t('product.select_variant')} open={isModalOpen} onCancel={() => setIsModalOpen(false)} onOk={confirmAdd} okText={t('product.add') as any}>
      <div className="flex flex-col gap-3">
        <Select placeholder={t('product.select_variant_placeholder')} value={selectedVariant ?? undefined} onChange={(v) => setSelectedVariant(Number(v))}>
          {product.variants?.map((v) => (
            <Select.Option key={v.id} value={v.id}>{`${v.size || ''} ${v.color || ''} — ${t('product.sku')}: ${v.sku} — ${v.stock} ${t('product.in_stock').toLowerCase()}`}</Select.Option>
          ))}
        </Select>
        <div>
          <span className="mr-2">{t('product.quantity')}:</span>
          <InputNumber min={1} max={999} value={quantity} onChange={(v) => setQuantity(Number(v))} />
        </div>
      </div>
    </Modal>
    </>
  );
};

export default ProductCard;
