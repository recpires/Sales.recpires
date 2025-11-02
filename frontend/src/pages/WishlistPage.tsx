import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Typography,
  Button,
  Empty,
  Row,
  Col,
  message,
  Spin,
  Alert,
} from "antd";
import {
  HeartOutlined,
  DeleteOutlined,
  ShoppingCartOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import wishlistService from "../services/wishlistService";
import { useCart } from "../context/CartContext";
import { NavBar } from "../components/navbar";
import { useSpring, animated } from "react-spring";

const { Title, Text } = Typography;

const WishlistPage: React.FC = () => {
  const navigate = useNavigate();
  const { dispatch } = useCart();
  const queryClient = useQueryClient();

  const fadeIn = useSpring({
    from: { opacity: 0, transform: "translateY(20px)" },
    to: { opacity: 1, transform: "translateY(0px)" },
    config: { tension: 280, friction: 60 },
  });

  // Fetch wishlist
  const {
    data: wishlistData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["wishlist"],
    queryFn: () => wishlistService.getWishlist(),
  });

  // Remove from wishlist mutation
  const removeMutation = useMutation({
    mutationFn: (id: number) => wishlistService.removeFromWishlist(id),
    onSuccess: () => {
      message.success("Produto removido dos favoritos");
      queryClient.invalidateQueries({ queryKey: ["wishlist"] });
    },
    onError: () => {
      message.error("Erro ao remover produto dos favoritos");
    },
  });

  const handleAddToCart = (wishlistItem: any) => {
    const product = wishlistItem.product_details;
    if (!product) return;

    dispatch({
      type: "ADD_ITEM",
      payload: {
        productId: product.id,
        variantId: null,
        quantity: 1,
        product,
      },
    });

    message.success("Produto adicionado ao carrinho!");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <div className="flex justify-center items-center h-96">
          <Spin size="large" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <div className="container mx-auto px-4 py-8">
          <Alert
            message="Erro ao carregar favoritos"
            description="Ocorreu um erro ao carregar sua lista de favoritos."
            type="error"
            showIcon
          />
        </div>
      </div>
    );
  }

  const wishlistItems = wishlistData?.results || [];

  if (wishlistItems.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <div className="container mx-auto px-4 py-12">
          <animated.div style={fadeIn}>
            <Card className="max-w-2xl mx-auto text-center py-12">
              <Empty
                image={
                  <HeartOutlined style={{ fontSize: 120, color: "#d9d9d9" }} />
                }
                description={
                  <div>
                    <Title level={3}>Sua lista de favoritos está vazia</Title>
                    <Text type="secondary" style={{ fontSize: 16 }}>
                      Adicione produtos aos favoritos para vê-los aqui!
                    </Text>
                  </div>
                }
              >
                <Button
                  type="primary"
                  size="large"
                  icon={<ShoppingCartOutlined />}
                  onClick={() => navigate("/home")}
                  className="mt-4"
                >
                  Explorar Produtos
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
          <div className="flex justify-between items-center mb-8">
            <div>
              <Title level={2} className="mb-2">
                ❤️ Meus Favoritos
              </Title>
              <Text type="secondary" style={{ fontSize: 16 }}>
                {wishlistItems.length}{" "}
                {wishlistItems.length === 1 ? "produto" : "produtos"} na sua
                lista de favoritos
              </Text>
            </div>
            <Button onClick={() => navigate("/home")}>
              Continuar Comprando
            </Button>
          </div>

          <Row gutter={[24, 24]}>
            {wishlistItems.map((item) => {
              const product = item.product_details;
              if (!product) return null;

              return (
                <Col key={item.id} xs={24} sm={12} md={8} lg={6}>
                  <Card
                    hoverable
                    className="shadow-md h-full"
                    cover={
                      <div className="relative">
                        {product.image ? (
                          <img
                            src={product.image}
                            alt={product.name}
                            className="w-full h-64 object-cover"
                          />
                        ) : (
                          <div className="w-full h-64 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-6xl">
                            📦
                          </div>
                        )}
                        <Button
                          danger
                          shape="circle"
                          icon={<DeleteOutlined />}
                          className="absolute top-2 right-2 shadow-lg"
                          onClick={() => removeMutation.mutate(item.id)}
                          loading={removeMutation.isPending}
                        />
                      </div>
                    }
                    actions={[
                      <Button
                        key="view"
                        type="link"
                        icon={<EyeOutlined />}
                        onClick={() => navigate(`/product/${product.id}`)}
                      >
                        Ver Detalhes
                      </Button>,
                      <Button
                        key="cart"
                        type="primary"
                        icon={<ShoppingCartOutlined />}
                        onClick={() => handleAddToCart(item)}
                      >
                        Adicionar
                      </Button>,
                    ]}
                  >
                    <Card.Meta
                      title={
                        <Text strong className="text-base line-clamp-2">
                          {product.name}
                        </Text>
                      }
                      description={
                        <div className="space-y-2">
                          <Text strong className="text-green-600 text-xl block">
                            R$ {Number(product.price ?? 0).toFixed(2)}
                          </Text>
                          {(product.stock ?? 0) > 0 ? (
                            <Text type="success" className="text-sm">
                              ✅ {product.stock ?? 0} em estoque
                            </Text>
                          ) : (
                            <Text type="danger" className="text-sm">
                              ❌ Esgotado
                            </Text>
                          )}
                        </div>
                      }
                    />
                  </Card>
                </Col>
              );
            })}
          </Row>
        </animated.div>
      </div>
    </div>
  );
};

export default WishlistPage;
