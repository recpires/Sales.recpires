import React, { useState, useEffect } from "react";
import {
  Form,
  Input,
  Button,
  Steps,
  Card,
  Typography,
  message,
  Row,
  Col,
  Divider,
  Select,
  Radio,
  Tag,
  Space,
  Spin,
} from "antd";
import {
  UserOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined,
  CreditCardOutlined,
  BarcodeOutlined,
  WalletOutlined,
  EnvironmentOutlined,
} from "@ant-design/icons";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useSpring, animated } from "react-spring";
import ApiErrorAlert from "../components/common/ApiErrorAlert";
import orderService from "../services/orderService";
import cepService from "../services/cepService";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { NavBar } from "../components/navbar";

const { Title, Text } = Typography;

// Schema de validação com Zod
const checkoutSchema = z.object({
  customer_name: z.string().min(3, "Nome deve ter no mínimo 3 caracteres"),
  customer_email: z.string().email("Email inválido"),
  customer_phone: z
    .string()
    .min(10, "Telefone deve ter no mínimo 10 caracteres"),
  cep: z.string().min(8, "CEP inválido"),
  street: z.string().min(3, "Rua é obrigatória"),
  number: z.string().min(1, "Número é obrigatório"),
  complement: z.string().optional(),
  neighborhood: z.string().min(3, "Bairro é obrigatório"),
  city: z.string().min(3, "Cidade é obrigatória"),
  state: z.string().length(2, "Estado deve ter 2 letras"),
  payment_method: z.enum(["credit_card", "debit_card", "pix", "boleto"], {
    errorMap: () => ({ message: "Selecione um método de pagamento" }),
  }),
});

type CheckoutFormData = z.infer<typeof checkoutSchema>;

const CheckoutPage: React.FC = () => {
  type ApiError = unknown;
  const [error, setError] = useState<ApiError>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingCep, setLoadingCep] = useState(false);
  const [shippingCost, setShippingCost] = useState(0);
  const [shippingDays, setShippingDays] = useState(0);
  const [shippingType, setShippingType] = useState("");
  const { state, dispatch, getTotal } = useCart();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Redireciona se o carrinho estiver vazio
  useEffect(() => {
    if (state.items.length === 0 && currentStep === 0) {
      message.warning("Seu carrinho está vazio!");
      navigate("/home");
    }
  }, [state.items.length, currentStep, navigate]);

  const {
    control,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<CheckoutFormData>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      customer_name: "",
      customer_email: "",
      customer_phone: "",
      cep: "",
      street: "",
      number: "",
      complement: "",
      neighborhood: "",
      city: "",
      state: "",
      payment_method: "pix" as any,
    },
  });

  const cepValue = watch("cep");

  // Busca endereço pelo CEP
  const handleCepBlur = async () => {
    const cep = cepValue?.replace(/\D/g, "");

    if (!cep || cep.length !== 8) return;

    setLoadingCep(true);
    try {
      const address = await cepService.fetchAddress(cep);

      // Preenche os campos automaticamente
      setValue("street", address.logradouro);
      setValue("neighborhood", address.bairro);
      setValue("city", address.localidade);
      setValue("state", address.uf);

      // Calcula o frete
      const shipping = cepService.calculateShipping(cep, getTotal());
      setShippingCost(shipping.value);
      setShippingDays(shipping.days);
      setShippingType(shipping.type);

      message.success("Endereço encontrado!");
    } catch (err: any) {
      message.error(err.message || "Erro ao buscar CEP");
    } finally {
      setLoadingCep(false);
    }
  };

  // Animação de fade-in
  const fadeIn = useSpring({
    from: { opacity: 0, transform: "translateY(20px)" },
    to: { opacity: 1, transform: "translateY(0px)" },
    config: { tension: 280, friction: 60 },
  });

  const onSubmit = async (data: CheckoutFormData) => {
    setError(null);
    setLoading(true);

    const items = state.items.map((i) => ({
      product: i.productId,
      variant: i.variantId || null,
      quantity: i.quantity,
    }));

    // Monta endereço completo
    const fullAddress = `${data.street}, ${data.number}${
      data.complement ? `, ${data.complement}` : ""
    }, ${data.neighborhood}, ${data.city}/${data.state}, CEP: ${data.cep}`;

    const payload = {
      customer_name: data.customer_name,
      customer_email: data.customer_email,
      customer_phone: data.customer_phone,
      shipping_address: fullAddress,
      status: "pending",
      items,
    };

    try {
      const res = await orderService.createOrder(payload);
      dispatch({ type: "CLEAR_CART" });
      message.success(t("checkout.order_created", { id: res.id }));
      setCurrentStep(1);
      setTimeout(() => navigate("/sales"), 3000);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      title: "Entrega",
      icon: <UserOutlined />,
    },
    {
      title: "Confirmação",
      icon: <CheckCircleOutlined />,
    },
  ];

  const renderInfoStep = () => (
    <animated.div style={fadeIn}>
      <Row gutter={24}>
        {/* Formulário de Entrega */}
        <Col xs={24} lg={14}>
          <Card className="mb-4">
            <Title level={4}>👤 Informações Pessoais</Title>
            <ApiErrorAlert error={error} />
            <Form layout="vertical" onFinish={handleSubmit(onSubmit)}>
              <Form.Item
                label="Nome Completo"
                validateStatus={errors.customer_name ? "error" : ""}
                help={errors.customer_name?.message}
              >
                <Controller
                  name="customer_name"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      placeholder="Seu nome completo"
                      size="large"
                    />
                  )}
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="Email"
                    validateStatus={errors.customer_email ? "error" : ""}
                    help={errors.customer_email?.message}
                  >
                    <Controller
                      name="customer_email"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          placeholder="seu@email.com"
                          type="email"
                          size="large"
                        />
                      )}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="Telefone"
                    validateStatus={errors.customer_phone ? "error" : ""}
                    help={errors.customer_phone?.message}
                  >
                    <Controller
                      name="customer_phone"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          placeholder="(11) 98765-4321"
                          size="large"
                        />
                      )}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>

          <Card className="mb-4">
            <Title level={4}>
              <EnvironmentOutlined /> Endereço de Entrega
            </Title>

            <Form layout="vertical" onFinish={handleSubmit(onSubmit)}>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="CEP"
                    validateStatus={errors.cep ? "error" : ""}
                    help={errors.cep?.message}
                  >
                    <Controller
                      name="cep"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          placeholder="00000-000"
                          size="large"
                          maxLength={9}
                          onBlur={handleCepBlur}
                          suffix={loadingCep && <Spin size="small" />}
                        />
                      )}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  {shippingType && (
                    <div className="mt-8">
                      <Tag
                        color={shippingCost === 0 ? "green" : "blue"}
                        className="text-sm py-1 px-3"
                      >
                        {shippingType}:{" "}
                        {shippingCost === 0
                          ? "GRÁTIS"
                          : `R$ ${shippingCost.toFixed(2)}`}
                      </Tag>
                      <Text type="secondary" className="text-xs block mt-1">
                        Entrega em até {shippingDays} dias úteis
                      </Text>
                    </div>
                  )}
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={18}>
                  <Form.Item
                    label="Rua"
                    validateStatus={errors.street ? "error" : ""}
                    help={errors.street?.message}
                  >
                    <Controller
                      name="street"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          placeholder="Nome da rua"
                          size="large"
                        />
                      )}
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    label="Número"
                    validateStatus={errors.number ? "error" : ""}
                    help={errors.number?.message}
                  >
                    <Controller
                      name="number"
                      control={control}
                      render={({ field }) => (
                        <Input {...field} placeholder="123" size="large" />
                      )}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                label="Complemento (opcional)"
                validateStatus={errors.complement ? "error" : ""}
                help={errors.complement?.message}
              >
                <Controller
                  name="complement"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      placeholder="Apto, bloco, etc."
                      size="large"
                    />
                  )}
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="Bairro"
                    validateStatus={errors.neighborhood ? "error" : ""}
                    help={errors.neighborhood?.message}
                  >
                    <Controller
                      name="neighborhood"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          placeholder="Nome do bairro"
                          size="large"
                        />
                      )}
                    />
                  </Form.Item>
                </Col>
                <Col span={10}>
                  <Form.Item
                    label="Cidade"
                    validateStatus={errors.city ? "error" : ""}
                    help={errors.city?.message}
                  >
                    <Controller
                      name="city"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          placeholder="Nome da cidade"
                          size="large"
                        />
                      )}
                    />
                  </Form.Item>
                </Col>
                <Col span={2}>
                  <Form.Item
                    label="UF"
                    validateStatus={errors.state ? "error" : ""}
                    help={errors.state?.message}
                  >
                    <Controller
                      name="state"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          placeholder="SP"
                          size="large"
                          maxLength={2}
                        />
                      )}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>

          <Card className="mb-4">
            <Title level={4}>💳 Forma de Pagamento</Title>
            <Form layout="vertical" onFinish={handleSubmit(onSubmit)}>
              <Form.Item
                validateStatus={errors.payment_method ? "error" : ""}
                help={errors.payment_method?.message}
              >
                <Controller
                  name="payment_method"
                  control={control}
                  render={({ field }) => (
                    <Radio.Group {...field} size="large" className="w-full">
                      <Space direction="vertical" className="w-full">
                        <Radio.Button
                          value="pix"
                          className="w-full h-16 text-left"
                        >
                          <Space>
                            <WalletOutlined
                              style={{ fontSize: 24, color: "#32bcad" }}
                            />
                            <div>
                              <div className="font-semibold">PIX</div>
                              <Text type="secondary" className="text-xs">
                                Aprovação imediata
                              </Text>
                            </div>
                          </Space>
                        </Radio.Button>

                        <Radio.Button
                          value="credit_card"
                          className="w-full h-16 text-left"
                        >
                          <Space>
                            <CreditCardOutlined
                              style={{ fontSize: 24, color: "#1890ff" }}
                            />
                            <div>
                              <div className="font-semibold">
                                Cartão de Crédito
                              </div>
                              <Text type="secondary" className="text-xs">
                                Parcelamento em até 12x
                              </Text>
                            </div>
                          </Space>
                        </Radio.Button>

                        <Radio.Button
                          value="debit_card"
                          className="w-full h-16 text-left"
                        >
                          <Space>
                            <CreditCardOutlined
                              style={{ fontSize: 24, color: "#52c41a" }}
                            />
                            <div>
                              <div className="font-semibold">
                                Cartão de Débito
                              </div>
                              <Text type="secondary" className="text-xs">
                                Débito em conta
                              </Text>
                            </div>
                          </Space>
                        </Radio.Button>

                        <Radio.Button
                          value="boleto"
                          className="w-full h-16 text-left"
                        >
                          <Space>
                            <BarcodeOutlined
                              style={{ fontSize: 24, color: "#fa8c16" }}
                            />
                            <div>
                              <div className="font-semibold">
                                Boleto Bancário
                              </div>
                              <Text type="secondary" className="text-xs">
                                Vencimento em 3 dias úteis
                              </Text>
                            </div>
                          </Space>
                        </Radio.Button>
                      </Space>
                    </Radio.Group>
                  )}
                />
              </Form.Item>

              <Row gutter={16} style={{ marginTop: 24 }}>
                <Col span={12}>
                  <Button
                    size="large"
                    block
                    icon={<ArrowLeftOutlined />}
                    onClick={() => navigate("/cart")}
                  >
                    Voltar ao Carrinho
                  </Button>
                </Col>
                <Col span={12}>
                  <Button
                    type="primary"
                    size="large"
                    block
                    htmlType="submit"
                    loading={loading}
                  >
                    Finalizar Pedido
                  </Button>
                </Col>
              </Row>
            </Form>
          </Card>
        </Col>

        {/* Resumo do Pedido */}
        <Col xs={24} lg={10}>
          <Card className="sticky top-24">
            <Title level={4}>📋 Resumo do Pedido</Title>
            <Divider />

            <div className="space-y-3 mb-4">
              {state.items.map((item) => {
                const product = item.product;
                const variant =
                  product?.variants?.find((v) => v.id === item.variantId) ??
                  null;
                const unitPrice = variant
                  ? Number(variant.price)
                  : product
                  ? Number(product.price)
                  : 0;

                return (
                  <div
                    key={`${item.productId}-${item.variantId}`}
                    className="flex gap-3 pb-3 border-b border-gray-100"
                  >
                    {product?.image ? (
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-16 h-16 object-cover rounded"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-gray-100 rounded flex items-center justify-center text-2xl">
                        📦
                      </div>
                    )}
                    <div className="flex-1">
                      <Text strong className="text-sm">
                        {product?.name}
                      </Text>
                      {variant && (
                        <div>
                          <Text type="secondary" className="text-xs">
                            {variant.size}{" "}
                            {variant.color ? `• ${variant.color}` : ""}
                          </Text>
                        </div>
                      )}
                      <div className="flex justify-between mt-1">
                        <Text type="secondary" className="text-xs">
                          Qtd: {item.quantity}
                        </Text>
                        <Text strong className="text-sm">
                          R$ {(unitPrice * item.quantity).toFixed(2)}
                        </Text>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <Divider />

            <Row justify="space-between" className="mb-2">
              <Col>
                <Text>
                  Subtotal ({state.items.length}{" "}
                  {state.items.length === 1 ? "item" : "itens"}):
                </Text>
              </Col>
              <Col>
                <Text strong>R$ {getTotal().toFixed(2)}</Text>
              </Col>
            </Row>

            <Row justify="space-between" className="mb-4">
              <Col>
                <Text>Frete:</Text>
              </Col>
              <Col>
                {shippingCost === 0 ? (
                  <Tag color="green">GRÁTIS</Tag>
                ) : shippingType ? (
                  <Text strong>R$ {shippingCost.toFixed(2)}</Text>
                ) : (
                  <Text type="secondary" className="text-xs">
                    Informe o CEP
                  </Text>
                )}
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
                  R$ {(getTotal() + shippingCost).toFixed(2)}
                </Text>
              </Col>
            </Row>

            <Divider />

            <div className="bg-blue-50 p-3 rounded-lg">
              <Text className="text-xs">
                <div className="flex items-start gap-2">
                  <span>🔒</span>
                  <div>
                    <Text strong className="text-xs">
                      Pagamento Seguro
                    </Text>
                    <br />
                    <Text type="secondary" className="text-xs">
                      Seus dados estão protegidos
                    </Text>
                  </div>
                </div>
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </animated.div>
  );

  const renderConfirmationStep = () => (
    <animated.div style={fadeIn}>
      <Card
        style={{
          textAlign: "center",
          padding: "60px 40px",
          maxWidth: 600,
          margin: "0 auto",
        }}
      >
        <CheckCircleOutlined
          style={{ fontSize: 96, color: "#52c41a", marginBottom: 32 }}
        />
        <Title level={2}>🎉 Pedido Realizado com Sucesso!</Title>
        <Text
          type="secondary"
          style={{ fontSize: 18, display: "block", marginTop: 16 }}
        >
          Obrigado por comprar conosco!
        </Text>
        <Text
          type="secondary"
          style={{ fontSize: 14, display: "block", marginTop: 8 }}
        >
          Você receberá um email de confirmação em breve.
        </Text>
        <Divider />
        <Text style={{ fontSize: 14 }}>
          Redirecionando para a página de vendas...
        </Text>
      </Card>
    </animated.div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <div className="container mx-auto px-4 py-8">
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <Title level={2} className="mb-2">
            Finalizar Compra
          </Title>
          <Text type="secondary" className="mb-6 block">
            Preencha os dados de entrega para concluir seu pedido
          </Text>
          <Steps
            current={currentStep}
            items={steps}
            style={{ marginBottom: 32 }}
          />

          {currentStep === 0 && renderInfoStep()}
          {currentStep === 1 && renderConfirmationStep()}
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
