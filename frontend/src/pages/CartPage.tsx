import React from "react";
import {
  Card,
  Typography,
  Button,
  List,
  InputNumber,
  Empty,
  Row,
  Col,
  Divider,
  Tag,
} from "antd";
import {
  ShoppingCartOutlined,
  DeleteOutlined,
  ArrowRightOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useSpring, animated } from "react-spring";
import { useCart } from "../context/CartContext";
import { useTranslation } from "react-i18next";
import { NavBar } from "../components/navbar";

const { Title, Text } = Typography;

const CartPage: React.FC = () => {
  const { state, dispatch, getTotal } = useCart();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Animação de fade-in
  const fadeIn = useSpring({
    from: { opacity: 0, transform: "translateY(20px)" },
    to: { opacity: 1, transform: "translateY(0px)" },
    config: { tension: 280, friction: 60 },
  });

  const handleContinueShopping = () => {
    navigate("/home");
  };

  const handleProceedToShipping = () => {
    navigate("/checkout");
  };

  if (state.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <div className="container mx-auto px-4 py-12">
          <animated.div style={fadeIn}>
            <Card className="max-w-2xl mx-auto text-center py-12">
              <Empty
                image={
                  <ShoppingCartOutlined
                    style={{ fontSize: 120, color: "#d9d9d9" }}
                  />
                }
                description={
                  <div>
                    <Title level={3}>Seu carrinho está vazio</Title>
                    <Text type="secondary" style={{ fontSize: 16 }}>
                      Adicione produtos incríveis ao seu carrinho!
                    </Text>
                  </div>
                }
              >
                <Button
                  type="primary"
                  size="large"
                  icon={<ShoppingCartOutlined />}
                  onClick={handleContinueShopping}
                  className="mt-4"
                >
                  Continuar Comprando
                </Button>
              </Empty>
            </Card>
          </animated.div>
        </div>
      </div>
    );
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
                <Title level={4}>
                  Itens no Carrinho ({state.items.length})
                </Title>
                <List
                  itemLayout="horizontal"
                  dataSource={state.items}
                  renderItem={(item) => {
                    const product = item.product;
                    const variant =
                      product?.variants?.find((v) => v.id === item.variantId) ??
                      null;
                    const unitPrice = variant
                      ? Number(variant.price)
                      : product
                      ? Number(product.price)
                      : 0;
                    const subtotal = unitPrice * item.quantity;

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
                                type: "REMOVE_ITEM",
                                payload: {
                                  productId: item.productId,
                                  variantId: item.variantId,
                                },
                              })
                            }
                          >
                            Remover
                          </Button>,
                        ]}
                      >
                        <List.Item.Meta
                          avatar={
                            product?.image ? (
                              <img
                                src={product.image}
                                alt={product.name}
                                style={{
                                  width: 100,
                                  height: 100,
                                  objectFit: "cover",
                                  borderRadius: 8,
                                  border: "1px solid #f0f0f0",
                                }}
                              />
                            ) : (
                              <div
                                style={{
                                  width: 100,
                                  height: 100,
                                  background:
                                    "linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)",
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  borderRadius: 8,
                                  fontSize: 40,
                                }}
                              >
                                📦
                              </div>
                            )
                          }
                          title={
                            <div>
                              <Text strong style={{ fontSize: 18 }}>
                                {product?.name ?? `Produto ${item.productId}`}
                              </Text>
                              {product?.seller_name && (
                                <div className="mt-1">
                                  <Tag color="blue" className="text-xs">
                                    Vendedor: {product.seller_name}
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
                                    Variante: {variant.size || ""}{" "}
                                    {variant.color ? `• ${variant.color}` : ""}
                                  </Text>
                                  <br />
                                  <Text type="secondary" className="text-xs">
                                    SKU: {variant.sku}
                                  </Text>
                                </div>
                              )}
                              <div className="flex items-center gap-4 mt-3">
                                <div>
                                  <Text type="secondary" className="text-sm">
                                    Preço unitário:
                                  </Text>
                                  <br />
                                  <Text
                                    strong
                                    style={{ fontSize: 18, color: "#52c41a" }}
                                  >
                                    R$ {unitPrice.toFixed(2)}
                                  </Text>
                                </div>
                                <div>
                                  <Text
                                    type="secondary"
                                    className="text-sm block mb-1"
                                  >
                                    Quantidade:
                                  </Text>
                                  <InputNumber
                                    min={1}
                                    max={99}
                                    value={item.quantity}
                                    onChange={(val: number | null) =>
                                      dispatch({
                                        type: "SET_QUANTITY",
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
                                  <Text type="secondary" className="text-sm">
                                    Subtotal:
                                  </Text>
                                  <br />
                                  <Text
                                    strong
                                    style={{ fontSize: 20, color: "#1890ff" }}
                                  >
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
                <Title level={4}>Resumo do Pedido</Title>
                <Divider />

                <div className="space-y-4">
                  <Row justify="space-between">
                    <Col>
                      <Text>
                        Subtotal ({state.items.length}{" "}
                        {state.items.length === 1 ? "item" : "itens"}):
                      </Text>
                    </Col>
                    <Col>
                      <Text strong style={{ fontSize: 16 }}>
                        R$ {getTotal().toFixed(2)}
                      </Text>
                    </Col>
                  </Row>

                  <Row justify="space-between">
                    <Col>
                      <Text>Frete:</Text>
                    </Col>
                    <Col>
                      <Tag color="green">GRÁTIS</Tag>
                    </Col>
                  </Row>

                  <Divider />

                  <Row justify="space-between" align="middle">
                    <Col>
                      <Text strong style={{ fontSize: 18 }}>
                        Total:
                      </Text>
                    </Col>
                    <Col>
                      <Text strong style={{ fontSize: 24, color: "#52c41a" }}>
                        R$ {getTotal().toFixed(2)}
                      </Text>
                    </Col>
                  </Row>

                  <Button
                    type="primary"
                    size="large"
                    block
                    icon={<ArrowRightOutlined />}
                    onClick={handleProceedToShipping}
                    className="mt-6"
                    style={{ height: 50, fontSize: 16 }}
                  >
                    Finalizar Compra
                  </Button>

                  <Button
                    type="default"
                    size="large"
                    block
                    onClick={handleContinueShopping}
                  >
                    Continuar Comprando
                  </Button>

                  <Divider />

                  {/* Informações de Segurança */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <Text className="text-sm">
                      <div className="flex items-start gap-2">
                        <span className="text-lg">🔒</span>
                        <div>
                          <Text strong className="text-sm">
                            Compra 100% Segura
                          </Text>
                          <br />
                          <Text type="secondary" className="text-xs">
                            Seus dados estão protegidos
                          </Text>
                        </div>
                      </div>
                    </Text>
                  </div>

                  <div className="bg-green-50 p-4 rounded-lg">
                    <Text className="text-sm">
                      <div className="flex items-start gap-2">
                        <span className="text-lg">🚚</span>
                        <div>
                          <Text strong className="text-sm">
                            Frete Grátis
                          </Text>
                          <br />
                          <Text type="secondary" className="text-xs">
                            Para todo o Brasil
                          </Text>
                        </div>
                      </div>
                    </Text>
                  </div>
                </div>
              </Card>
            </Col>
          </Row>
        </animated.div>
      </div>
    </div>
  );
};

export default CartPage;
