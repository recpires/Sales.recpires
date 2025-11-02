import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  Typography,
  Button,
  InputNumber,
  Tag,
  Rate,
  Divider,
  Row,
  Col,
  Tabs,
  Avatar,
  message,
  Spin,
  Alert,
  Badge,
} from "antd";
import {
  ShoppingCartOutlined,
  HeartOutlined,
  HeartFilled,
  StarFilled,
  ArrowLeftOutlined,
  ShopOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import productService from "../services/productService";
import reviewService from "../services/reviewService";
import wishlistService from "../services/wishlistService";
import { useCart } from "../context/CartContext";
import { NavBar } from "../components/navbar";
import { Review } from "../types/review";

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { dispatch } = useCart();
  const queryClient = useQueryClient();

  const [quantity, setQuantity] = useState(1);
  const [selectedVariantId, setSelectedVariantId] = useState<number | null>(
    null
  );
  const [isInWishlist, setIsInWishlist] = useState(false);

  // Fetch product details
  const {
    data: product,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["product", id],
    queryFn: () => productService.getProduct(Number(id)),
    enabled: !!id,
  });

  // Fetch reviews
  const { data: reviewsData } = useQuery({
    queryKey: ["reviews", id],
    queryFn: () => reviewService.getReviews(Number(id)),
    enabled: !!id,
  });

  // Wishlist mutation
  const wishlistMutation = useMutation({
    mutationFn: (productId: number) =>
      wishlistService.toggleWishlist(productId),
    onSuccess: (data) => {
      setIsInWishlist(data.action === "added");
      message.success(data.message);
      queryClient.invalidateQueries({ queryKey: ["wishlist"] });
    },
  });

  const handleAddToCart = () => {
    if (!product) return;

    dispatch({
      type: "ADD_ITEM",
      payload: {
        productId: product.id,
        variantId: selectedVariantId,
        quantity,
        product,
      },
    });

    message.success("Produto adicionado ao carrinho!");
  };

  const handleToggleWishlist = () => {
    if (!product) return;
    wishlistMutation.mutate(product.id);
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

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <div className="container mx-auto px-4 py-8">
          <Alert
            message="Erro ao carregar produto"
            description="Produto não encontrado ou ocorreu um erro."
            type="error"
            showIcon
          />
          <Button onClick={() => navigate("/home")} className="mt-4">
            Voltar para Home
          </Button>
        </div>
      </div>
    );
  }

  const selectedVariant = selectedVariantId
    ? product.variants?.find((v) => v.id === selectedVariantId)
    : null;

  const currentPrice = selectedVariant
    ? Number(selectedVariant.price ?? product.price ?? 0)
    : Number(product.price ?? 0);

  // Ensure currentStock is always a number
  const currentStock = Number(selectedVariant?.stock ?? product.stock ?? 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="mb-6">
          <Button
            type="link"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate("/home")}
          >
            Voltar para produtos
          </Button>
        </div>

        <Row gutter={32}>
          {/* Product Image */}
          <Col xs={24} md={10}>
            <Card className="shadow-lg">
              {product.image ? (
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full h-96 object-cover rounded-lg"
                />
              ) : (
                <div className="w-full h-96 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center text-8xl">
                  📦
                </div>
              )}

              {/* Thumbnail variants (if multiple images available) */}
              {product.variants && product.variants.length > 0 && (
                <div className="flex gap-2 mt-4 overflow-x-auto">
                  {product.variants
                    .filter((v) => v.image)
                    .map((variant) => (
                      <img
                        key={variant.id}
                        src={variant.image || ""}
                        alt={`${variant?.color ?? ""} ${variant?.size ?? ""}`}
                        className={`w-16 h-16 object-cover rounded cursor-pointer border-2 ${
                          selectedVariantId === variant.id
                            ? "border-blue-500"
                            : "border-gray-200"
                        }`}
                        onClick={() => setSelectedVariantId(variant.id)}
                      />
                    ))}
                </div>
              )}
            </Card>
          </Col>

          {/* Product Info */}
          <Col xs={24} md={14}>
            <Card className="shadow-lg">
              {/* Store Info */}
              {product.store_name && (
                <div className="mb-4">
                  <Tag icon={<ShopOutlined />} color="blue">
                    {product.store_name}
                  </Tag>
                </div>
              )}

              <Title level={2} className="mb-2">
                {product.name}
              </Title>

              {/* Rating */}
              {product.average_rating && product.average_rating > 0 && (
                <div className="flex items-center gap-2 mb-4">
                  <Rate disabled value={product.average_rating} allowHalf />
                  <Text strong>{product.average_rating.toFixed(1)}</Text>
                  <Text type="secondary">
                    ({product.review_count || 0} avaliações)
                  </Text>
                </div>
              )}

              {/* Price */}
              <div className="mb-6">
                <Text className="text-4xl font-bold text-green-600">
                  R$ {currentPrice.toFixed(2)}
                </Text>
              </div>

              {/* Description */}
              <Divider />
              <Paragraph>
                {product.description || "Sem descrição disponível."}
              </Paragraph>
              <Divider />

              {/* Variants Selection */}
              {product.variants && product.variants.length > 0 && (
                <div className="mb-6">
                  <Text strong className="block mb-2">
                    Selecione uma variação:
                  </Text>
                  <div className="flex flex-wrap gap-2">
                    {product.variants.map((variant) => (
                      <Button
                        key={variant.id}
                        type={
                          selectedVariantId === variant.id
                            ? "primary"
                            : "default"
                        }
                        onClick={() => setSelectedVariantId(variant.id)}
                        disabled={!variant.is_active || variant.stock === 0}
                      >
                        {variant?.size ?? ""}{" "}
                        {variant?.color ? `• ${variant.color}` : ""}
                        {variant.stock === 0 && " (Esgotado)"}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Stock Info */}
              <div className="mb-4">
                {currentStock > 0 ? (
                  <Badge
                    status="success"
                    text={`${currentStock} unidades disponíveis`}
                  />
                ) : (
                  <Badge status="error" text="Produto esgotado" />
                )}
              </div>

              {/* Quantity Selector */}
              {currentStock > 0 && (
                <div className="mb-6">
                  <Text strong className="block mb-2">
                    Quantidade:
                  </Text>
                  <InputNumber
                    min={1}
                    max={currentStock}
                    value={quantity}
                    onChange={(val) => setQuantity(val || 1)}
                    size="large"
                    className="w-32"
                  />
                </div>
              )}

              {/* Action Buttons */}
              <Row gutter={16}>
                <Col span={18}>
                  <Button
                    type="primary"
                    size="large"
                    block
                    icon={<ShoppingCartOutlined />}
                    onClick={handleAddToCart}
                    disabled={
                      currentStock === 0 ||
                      (product.variants &&
                        product.variants.length > 0 &&
                        !selectedVariantId)
                    }
                  >
                    Adicionar ao Carrinho
                  </Button>
                </Col>
                <Col span={6}>
                  <Button
                    size="large"
                    block
                    icon={isInWishlist ? <HeartFilled /> : <HeartOutlined />}
                    onClick={handleToggleWishlist}
                    danger={isInWishlist}
                    loading={wishlistMutation.isPending}
                  >
                    Favoritar
                  </Button>
                </Col>
              </Row>

              {/* Additional Info */}
              <Divider />
              <Row gutter={16} className="text-center">
                <Col span={8}>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <Text strong className="block text-blue-600">
                      🚚 Frete Grátis
                    </Text>
                    <Text type="secondary" className="text-xs">
                      Para todo Brasil
                    </Text>
                  </div>
                </Col>
                <Col span={8}>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <Text strong className="block text-green-600">
                      🔒 Compra Segura
                    </Text>
                    <Text type="secondary" className="text-xs">
                      Dados protegidos
                    </Text>
                  </div>
                </Col>
                <Col span={8}>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <Text strong className="block text-orange-600">
                      ↩️ Devolução Fácil
                    </Text>
                    <Text type="secondary" className="text-xs">
                      Até 30 dias
                    </Text>
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

        {/* Reviews Section */}
        <Card className="mt-8 shadow-lg">
          <Tabs defaultActiveKey="reviews">
            <TabPane
              tab={`Avaliações (${reviewsData?.count || 0})`}
              key="reviews"
            >
              {reviewsData && reviewsData.results.length > 0 ? (
                <div className="space-y-4">
                  {reviewsData.results.map((review: Review) => (
                    <Card key={review.id} className="bg-gray-50">
                      <div className="flex items-start gap-4">
                        <Avatar size={48}>
                          {review.user_first_name?.charAt(0) ||
                            review.user_name?.charAt(0)}
                        </Avatar>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Text strong>
                              {review.user_first_name || review.user_name}
                            </Text>
                            {review.is_verified_purchase && (
                              <Tag color="green" className="text-xs">
                                Compra Verificada
                              </Tag>
                            )}
                          </div>
                          <Rate
                            disabled
                            value={review.rating}
                            className="text-sm"
                          />
                          {review.title && (
                            <Title level={5} className="mt-2">
                              {review.title}
                            </Title>
                          )}
                          <Paragraph className="mt-2">
                            {review.comment}
                          </Paragraph>
                          <Text type="secondary" className="text-xs">
                            {new Date(review.created_at).toLocaleDateString(
                              "pt-BR"
                            )}
                          </Text>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <StarFilled style={{ fontSize: 64, color: "#d9d9d9" }} />
                  <Title level={4} className="mt-4">
                    Nenhuma avaliação ainda
                  </Title>
                  <Text type="secondary">
                    Seja o primeiro a avaliar este produto!
                  </Text>
                </div>
              )}
            </TabPane>

            <TabPane tab="Especificações" key="specs">
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Text strong>SKU:</Text> <Text>{product.sku || "N/A"}</Text>
                </Col>
                <Col span={12}>
                  <Text strong>Cor:</Text> <Text>{product.color || "N/A"}</Text>
                </Col>
                <Col span={12}>
                  <Text strong>Tamanho:</Text>{" "}
                  <Text>{product.size || "N/A"}</Text>
                </Col>
                <Col span={12}>
                  <Text strong>Status:</Text>{" "}
                  <Badge
                    status={product.is_active ? "success" : "error"}
                    text={product.is_active ? "Ativo" : "Inativo"}
                  />
                </Col>
              </Row>
            </TabPane>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

export default ProductDetailPage;
