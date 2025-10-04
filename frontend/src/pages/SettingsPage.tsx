import { useState } from 'react';
import { Card, Form, Input, Button, Switch, Select, Divider, message } from 'antd';
import { UserOutlined, LockOutlined, BellOutlined, GlobalOutlined } from '@ant-design/icons';
import { NavBar } from '../components/navbar';
import { Aside } from '../components/aside';
import authService from '../services/authService';

const SettingsPage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const isAdmin = user?.is_staff || user?.is_superuser;

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  const handleSaveProfile = (values: any) => {
    console.log('Profile values:', values);
    message.success('Perfil atualizado com sucesso!');
  };

  const handleChangePassword = (values: any) => {
    console.log('Password values:', values);
    message.success('Senha alterada com sucesso!');
  };

  const handleSaveNotifications = (values: any) => {
    console.log('Notification values:', values);
    message.success('Configurações de notificação salvas!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="flex">
        {isAdmin && <Aside isOpen={isAsideOpen} onToggle={toggleAside} />}

        <main className="flex-1 p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Configurações</h1>
            <p className="text-gray-600">Gerencie suas preferências e configurações</p>
          </div>

          <div className="max-w-4xl">
            {/* Perfil do Usuário */}
            <Card
              title={
                <span className="flex items-center gap-2">
                  <UserOutlined />
                  Perfil do Usuário
                </span>
              }
              className="mb-6"
            >
              <Form layout="vertical" onFinish={handleSaveProfile} initialValues={{
                firstName: user?.first_name || '',
                lastName: user?.last_name || '',
                email: user?.email || '',
                username: user?.username || '',
              }}>
                <Form.Item label="Nome" name="firstName">
                  <Input placeholder="Seu primeiro nome" />
                </Form.Item>
                <Form.Item label="Sobrenome" name="lastName">
                  <Input placeholder="Seu sobrenome" />
                </Form.Item>
                <Form.Item label="Email" name="email">
                  <Input type="email" placeholder="seu@email.com" />
                </Form.Item>
                <Form.Item label="Nome de Usuário" name="username">
                  <Input placeholder="nomedeusuario" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit">
                    Salvar Alterações
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            {/* Alterar Senha */}
            <Card
              title={
                <span className="flex items-center gap-2">
                  <LockOutlined />
                  Segurança
                </span>
              }
              className="mb-6"
            >
              <Form layout="vertical" onFinish={handleChangePassword}>
                <Form.Item label="Senha Atual" name="currentPassword">
                  <Input.Password placeholder="Digite sua senha atual" />
                </Form.Item>
                <Form.Item label="Nova Senha" name="newPassword">
                  <Input.Password placeholder="Digite a nova senha" />
                </Form.Item>
                <Form.Item label="Confirmar Nova Senha" name="confirmPassword">
                  <Input.Password placeholder="Confirme a nova senha" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit">
                    Alterar Senha
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            {/* Notificações */}
            <Card
              title={
                <span className="flex items-center gap-2">
                  <BellOutlined />
                  Notificações
                </span>
              }
              className="mb-6"
            >
              <Form layout="vertical" onFinish={handleSaveNotifications}>
                <Form.Item label="Notificações por Email" name="emailNotifications" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Divider />
                <Form.Item label="Notificações de Vendas" name="salesNotifications" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Divider />
                <Form.Item label="Notificações de Novos Clientes" name="clientNotifications" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Divider />
                <Form.Item label="Notificações de Relatórios" name="reportNotifications" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit">
                    Salvar Preferências
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            {/* Preferências do Sistema */}
            <Card
              title={
                <span className="flex items-center gap-2">
                  <GlobalOutlined />
                  Preferências do Sistema
                </span>
              }
            >
              <Form layout="vertical">
                <Form.Item label="Idioma" name="language">
                  <Select
                    defaultValue="pt-BR"
                    options={[
                      { value: 'pt-BR', label: 'Português (Brasil)' },
                      { value: 'en-US', label: 'English (US)' },
                      { value: 'es-ES', label: 'Español' },
                    ]}
                  />
                </Form.Item>
                <Form.Item label="Fuso Horário" name="timezone">
                  <Select
                    defaultValue="America/Sao_Paulo"
                    options={[
                      { value: 'America/Sao_Paulo', label: 'Brasília (GMT-3)' },
                      { value: 'America/New_York', label: 'New York (GMT-5)' },
                      { value: 'Europe/London', label: 'London (GMT+0)' },
                    ]}
                  />
                </Form.Item>
                <Form.Item>
                  <Button type="primary">Salvar Configurações</Button>
                </Form.Item>
              </Form>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SettingsPage;