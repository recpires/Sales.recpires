import { useState } from 'react';
import { Card, Table, Tag, Button, Space, Statistic, Row, Col } from 'antd';
import { ShoppingCartOutlined, DollarOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { NavBar } from '../components/navbar';
import { Aside } from '../components/aside';
import authService from '../services/authService';

const SalesPage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const isAdmin = user?.is_staff || user?.is_superuser;

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  // Dados mockados de exemplo
  const mockSales = [
    {
      key: '1',
      id: '#001',
      customer: 'João Silva',
      date: '2025-10-01',
      total: 'R$ 450,00',
      status: 'completed',
      items: 3,
    },
    {
      key: '2',
      id: '#002',
      customer: 'Maria Santos',
      date: '2025-10-02',
      total: 'R$ 780,00',
      status: 'pending',
      items: 5,
    },
    {
      key: '3',
      id: '#003',
      customer: 'Pedro Costa',
      date: '2025-10-03',
      total: 'R$ 1.200,00',
      status: 'processing',
      items: 8,
    },
  ];

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Cliente',
      dataIndex: 'customer',
      key: 'customer',
    },
    {
      title: 'Data',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: 'Itens',
      dataIndex: 'items',
      key: 'items',
    },
    {
      title: 'Total',
      dataIndex: 'total',
      key: 'total',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          completed: { color: 'success', text: 'Concluída' },
          pending: { color: 'warning', text: 'Pendente' },
          processing: { color: 'processing', text: 'Processando' },
        };
        return <Tag color={statusMap[status]?.color}>{statusMap[status]?.text}</Tag>;
      },
    },
    {
      title: 'Ações',
      key: 'actions',
      render: () => (
        <Space>
          <Button type="link" size="small">Ver Detalhes</Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="flex">
        {isAdmin && <Aside isOpen={isAsideOpen} onToggle={toggleAside} />}

        <main className="flex-1 p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Vendas</h1>
            <p className="text-gray-600">Gerencie todas as vendas do sistema</p>
          </div>

          {/* Estatísticas */}
          <Row gutter={16} className="mb-8">
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Total de Vendas"
                  value={156}
                  prefix={<ShoppingCartOutlined />}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Faturamento Total"
                  value={45890}
                  prefix={<DollarOutlined />}
                  precision={2}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Concluídas"
                  value={120}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Pendentes"
                  value={36}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Tabela de Vendas */}
          <Card title="Últimas Vendas" className="shadow-md">
            <Table
              columns={columns}
              dataSource={mockSales}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </main>
      </div>
    </div>
  );
};

export default SalesPage;
