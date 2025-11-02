import React, { useState } from "react";
import {
  Card,
  Typography,
  Table,
  Tag,
  Button,
  Empty,
  Spin,
  Space,
  Descriptions,
  Modal,
} from "antd";
import { EyeOutlined, ShoppingOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { useSpring, animated } from "react-spring";
import { NavBar } from "../components/navbar";
import { Aside } from "../components/aside";
import orderService from "../services/orderService";
import authService from "../services/authService";

const { Title, Text } = Typography;

interface OrderItem {
  id: number;
  product: number;
  product_name: string;
  variant: number | null;
  quantity: number;
  unit_price: string;
  subtotal: string;
}

interface Order {
  id: number;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  shipping_address: string;
  status: string;
  total_amount: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

const OrderHistoryPage: React.FC = () => {
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const user = authService.getCurrentUser();
  const isAdmin = user?.is_staff || user?.is_superuser;

  // Animação de fade-in
  const fadeIn = useSpring({
    from: { opacity: 0, transform: "translateY(20px)" },
    to: { opacity: 1, transform: "translateY(0px)" },
    config: { tension: 280, friction: 60 },
  });

  // Busca pedidos
  const { data, isLoading, error } = useQuery({
    queryKey: ["orders", user?.email],
    queryFn: async () => {
      const response = await orderService.getOrders();
      return response;
    },
  });

  const orders: Order[] = data?.results || data || [];

  // Filtra pedidos do usuário (se não for admin)
  const userOrders = isAdmin
    ? orders
    : orders.filter((order) => order.customer_email === user?.email);

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  const handleViewDetails = (order: Order) => {
    setSelectedOrder(order);
    setIsModalOpen(true);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: "orange",
      processing: "blue",
      shipped: "cyan",
      delivered: "green",
      cancelled: "red",
    };
    return colors[status] || "default";
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      pending: "Pendente",
      processing: "Processando",
      shipped: "Enviado",
      delivered: "Entregue",
      cancelled: "Cancelado",
    };
    return texts[status] || status;
  };

  const columns = [
    {
      title: "Pedido",
      dataIndex: "id",
      key: "id",
      render: (id: number) => <Text strong>#{id}</Text>,
    },
    {
      title: "Data",
      dataIndex: "created_at",
      key: "created_at",
      render: (date: string) => new Date(date).toLocaleDateString("pt-BR"),
    },
    {
      title: "Cliente",
      dataIndex: "customer_name",
      key: "customer_name",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: "Total",
      dataIndex: "total_amount",
      key: "total_amount",
      render: (amount: string) => (
        <Text strong style={{ fontSize: 16, color: "#52c41a" }}>
          R$ {parseFloat(amount).toFixed(2)}
        </Text>
      ),
    },
    {
      title: "Ações",
      key: "actions",
      render: (_: any, record: Order) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record)}
        >
          Ver Detalhes
        </Button>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <div className="flex">
        {isAdmin && <Aside isOpen={isAsideOpen} onToggle={toggleAside} />}

        <main className="flex-1 p-8">
          <animated.div style={fadeIn}>
            <div className="mb-6">
              <Title level={2}>
                <ShoppingOutlined /> Meus Pedidos
              </Title>
              <Text type="secondary">
                Acompanhe o histórico e status dos seus pedidos
              </Text>
            </div>

            <Card>
              {isLoading ? (
                <div className="flex justify-center items-center h-64">
                  <Spin size="large" />
                </div>
              ) : error ? (
                <Empty description="Erro ao carregar pedidos" />
              ) : userOrders.length === 0 ? (
                <Empty
                  image={
                    <ShoppingOutlined
                      style={{ fontSize: 80, color: "#d9d9d9" }}
                    />
                  }
                  description={
                    <div>
                      <Title level={4}>Nenhum pedido encontrado</Title>
                      <Text type="secondary">
                        Você ainda não realizou nenhum pedido.
                      </Text>
                    </div>
                  }
                />
              ) : (
                <Table
                  columns={columns}
                  dataSource={userOrders}
                  rowKey="id"
                  pagination={{ pageSize: 10 }}
                />
              )}
            </Card>
          </animated.div>
        </main>
      </div>

      {/* Modal de Detalhes do Pedido */}
      <Modal
        title={`Detalhes do Pedido #${selectedOrder?.id}`}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setIsModalOpen(false)}>
            Fechar
          </Button>,
        ]}
        width={700}
      >
        {selectedOrder && (
          <div>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="Status" span={2}>
                <Tag color={getStatusColor(selectedOrder.status)}>
                  {getStatusText(selectedOrder.status)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Data do Pedido">
                {new Date(selectedOrder.created_at).toLocaleString("pt-BR")}
              </Descriptions.Item>
              <Descriptions.Item label="Última Atualização">
                {new Date(selectedOrder.updated_at).toLocaleString("pt-BR")}
              </Descriptions.Item>
              <Descriptions.Item label="Cliente" span={2}>
                {selectedOrder.customer_name}
              </Descriptions.Item>
              <Descriptions.Item label="Email">
                {selectedOrder.customer_email}
              </Descriptions.Item>
              <Descriptions.Item label="Telefone">
                {selectedOrder.customer_phone}
              </Descriptions.Item>
              <Descriptions.Item label="Endereço de Entrega" span={2}>
                {selectedOrder.shipping_address}
              </Descriptions.Item>
            </Descriptions>

            <Title level={5} className="mt-6 mb-4">
              Itens do Pedido
            </Title>

            <Table
              dataSource={selectedOrder.items}
              rowKey="id"
              pagination={false}
              size="small"
              columns={[
                {
                  title: "Produto",
                  dataIndex: "product_name",
                  key: "product_name",
                },
                {
                  title: "Quantidade",
                  dataIndex: "quantity",
                  key: "quantity",
                  align: "center",
                },
                {
                  title: "Preço Unitário",
                  dataIndex: "unit_price",
                  key: "unit_price",
                  render: (price: string) =>
                    `R$ ${parseFloat(price).toFixed(2)}`,
                },
                {
                  title: "Subtotal",
                  dataIndex: "subtotal",
                  key: "subtotal",
                  render: (subtotal: string) => (
                    <Text strong>R$ {parseFloat(subtotal).toFixed(2)}</Text>
                  ),
                },
              ]}
            />

            <div className="mt-6 text-right">
              <Space direction="vertical" align="end">
                <Text style={{ fontSize: 18 }}>
                  Total do Pedido:{" "}
                  <Text strong style={{ fontSize: 24, color: "#52c41a" }}>
                    R$ {parseFloat(selectedOrder.total_amount).toFixed(2)}
                  </Text>
                </Text>
              </Space>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default OrderHistoryPage;
