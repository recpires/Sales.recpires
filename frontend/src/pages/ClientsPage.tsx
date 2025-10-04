import { useState } from 'react';
import { Card, Table, Button, Space, Tag, Avatar } from 'antd';
import { UserOutlined, PhoneOutlined, MailOutlined, PlusOutlined } from '@ant-design/icons';
import { NavBar } from '../components/navbar';
import { Aside } from '../components/aside';
import authService from '../services/authService';

const ClientsPage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const isAdmin = user?.is_staff || user?.is_superuser;

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  // Dados mockados de exemplo
  const mockClients = [
    {
      key: '1',
      name: 'João Silva',
      email: 'joao.silva@email.com',
      phone: '(11) 98765-4321',
      orders: 12,
      total: 'R$ 5.400,00',
      status: 'active',
    },
    {
      key: '2',
      name: 'Maria Santos',
      email: 'maria.santos@email.com',
      phone: '(21) 99876-5432',
      orders: 8,
      total: 'R$ 3.200,00',
      status: 'active',
    },
    {
      key: '3',
      name: 'Pedro Costa',
      email: 'pedro.costa@email.com',
      phone: '(31) 97654-3210',
      orders: 5,
      total: 'R$ 2.100,00',
      status: 'inactive',
    },
  ];

  const columns = [
    {
      title: 'Cliente',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <span>{name}</span>
        </Space>
      ),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      render: (email: string) => (
        <Space>
          <MailOutlined />
          {email}
        </Space>
      ),
    },
    {
      title: 'Telefone',
      dataIndex: 'phone',
      key: 'phone',
      render: (phone: string) => (
        <Space>
          <PhoneOutlined />
          {phone}
        </Space>
      ),
    },
    {
      title: 'Pedidos',
      dataIndex: 'orders',
      key: 'orders',
    },
    {
      title: 'Total Gasto',
      dataIndex: 'total',
      key: 'total',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'success' : 'default'}>
          {status === 'active' ? 'Ativo' : 'Inativo'}
        </Tag>
      ),
    },
    {
      title: 'Ações',
      key: 'actions',
      render: () => (
        <Space>
          <Button type="link" size="small">Ver Perfil</Button>
          <Button type="link" size="small">Editar</Button>
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
          <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Clientes</h1>
              <p className="text-gray-600">Gerencie sua base de clientes</p>
            </div>
            {isAdmin && (
              <Button type="primary" size="large" icon={<PlusOutlined />}>
                Novo Cliente
              </Button>
            )}
          </div>

          <Card className="shadow-md">
            <Table
              columns={columns}
              dataSource={mockClients}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </main>
      </div>
    </div>
  );
};

export default ClientsPage;