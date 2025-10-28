import React from 'react';
import { Card, Typography, Button, List, InputNumber, Empty, Row, Col, Divider, Tag } from 'antd';
import { ShoppingCartOutlined, DeleteOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useSpring, animated } from 'react-spring';
import { useCart } from '../context/CartContext';
// import { useTranslation } from 'react-i18next'; // Removido se 't' não for usado
import { NavBar } from '../components/navbar';
import { ProductVariant } from '../types/product'; // Import ProductVariant se não estiver global

const { Title, Text } = Typography;

const CartPage: React.FC = () => {
  // CORREÇÃO 5: Removido 't' se não for usado
  // const { t } = useTranslation();
  const { state, dispatch, getTotal } = useCart();
  const navigate = useNavigate();


  const fadeIn = useSpring({ /* ... animação ... */ });

  const handleContinueShopping = () => navigate('/home');
  const handleProceedToShipping = () => navigate('/checkout');

  if (state.items.length === 0) {
     return ( /* ... JSX para carrinho vazio ... */ );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <div className="container mx-auto px-4 py-8">
        <animated.div style={fadeIn}>
          <Title level={2} className="mb-6">
            <ShoppingCartOutlined /> Meu Carrinho
          </Title>

          <Row gutter={24}>
            {/* Lista de Produtos */}
            <Col xs={24} lg={16}>
              <Card>
                <Title level={4}>Itens no Carrinho ({state.items.length})</Title>
                <List
                  itemLayout="horizontal"
                  dataSource={state.items}
                  renderItem={(item) => {
                    const product = item.product; // Assumindo que CartItem tem 'product'

                    // Encontra a variante DENTRO do objeto 'product' que está no item do carrinho
                    const variant: ProductVariant | null | undefined = product?.variants?.find(
                      (v) => v.id === item.variantId
                    );

                    // Preço VEM DA VARIANTE encontrada
                    const unitPrice = variant ? Number(variant.price) : 0;
                    const subtotal = unitPrice * item.quantity;

                    // Prioriza imagem da variante, fallback para imagem do produto
                    const displayImage = variant?.image || product?.image;

                    return (
                      <List.Item
                        className="border-b border-gray-100 py-6"
                        actions={[
                          <Button
                            key="remove"
                            danger
                            type="text"
                            icon={<DeleteOutlined />}
                            onClick={() =>
                              dispatch({
                                type: 'REMOVE_ITEM',
                                payload: { productId: item.productId, variantId: item.variantId },
                              })
                            }
                          >
                            Remover
                          </Button>,
                        ]}
                      >
                        <List.Item.Meta
                          avatar={
                            displayImage ? (
                              <img src={displayImage} alt={product?.name ?? ''} /* style */ />
                            ) : (
                              <div /* style do placeholder */>📦</div>
                            )
                          }
                          title={
                            <div>
                              <Text strong style={{ fontSize: 18 }}>
                                {product?.name ?? `Produto ${item.productId}`}
                              </Text>
                              {/* CORREÇÃO 1: Usar store_name */}
                              {product?.store_name && (
                                <div className="mt-1">
                                  <Tag color="blue" className="text-xs">
                                    Vendedor: {product.store_name}
                                  </Tag>
                                </div>
                              )}
                            </div>
                          }
                          description={
                            <div className="mt-3">
                              {variant && (
                                <div className="mb-2">
                                  <Text type="secondary" className="text-sm">
                                    {/* CORREÇÃO 2: Usar display names (assumindo que existem no tipo ProductVariant) */}
                                    Variante: {variant.size_display || variant.size || ''} {variant.color_display || variant.color ? `• ${variant.color_display || variant.color}` : ''} {variant.model ? `• ${variant.model}`: ''}
                                  </Text>
                                  <br />
                                  <Text type="secondary" className="text-xs">
                                    SKU: {variant.sku}
                                  </Text>
                                </div>
                              )}
                              <div className="flex items-center gap-4 mt-3">
                                <div>
                                  <Text type="secondary" className="text-sm">Preço unitário:</Text><br />
                                  <Text strong style={{ fontSize: 18, color: '#52c41a' }}>
                                    R$ {unitPrice.toFixed(2)}
                                  </Text>
                                </div>
                                <div>
                                  <Text type="secondary" className="text-sm block mb-1">Quantidade:</Text>
                                  <InputNumber
                                    min={1}
                                    max={99} // Idealmente, usar variant?.stock como max
                                    value={item.quantity}
                                    onChange={(val: number | null) =>
                                      dispatch({
                                        // CORREÇÃO 3: Usar UPDATE_QUANTITY
                                        type: 'UPDATE_QUANTITY',
                                        // CORREÇÃO 4: Payload está correto para UPDATE_QUANTITY
                                        payload: {
                                          productId: item.productId,
                                          variantId: item.variantId,
                                          quantity: Number(val ?? 1),
                                        },
                                      })
                                    }
                                    size="large"
                                  />
                                </div>
                                <div>
                                  <Text type="secondary" className="text-sm">Subtotal:</Text><br />
                                  <Text strong style={{ fontSize: 20, color: '#1890ff' }}>
                                    R$ {subtotal.toFixed(2)}
                                  </Text>
                                </div>
                              </div>
                            </div>
                          }
                        />
                      </List.Item>
                    );
                  }}
                />
              </Card>
            </Col>

            {/* Resumo do Pedido */}
            <Col xs={24} lg={8}>
              <Card className="sticky top-24">
                 {/* ... JSX do Resumo do Pedido (sem erros reportados aqui) ... */}
                 <Title level={4}>Resumo do Pedido</Title>
                 <Divider />
                 {/* ... Conteúdo do resumo ... */}
                 <Row justify="space-between" align="middle">
                   <Col><Text strong style={{ fontSize: 18 }}>Total:</Text></Col>
                   <Col>
                     <Text strong style={{ fontSize: 24, color: '#52c41a' }}>
                       R$ {getTotal().toFixed(2)} {/* Usa getTotal do useCart */}
                     </Text>
                   </Col>
                 </Row>
                 <Button type="primary" size="large" block icon={<ArrowRightOutlined />} onClick={handleProceedToShipping} /* ... */>
                   Finalizar Compra
                 </Button>
                 {/* ... Restante do resumo ... */}
              </Card>
            </Col>
          </Row>
        </animated.div>
      </div>
    </div>
  );
};

export default CartPage;