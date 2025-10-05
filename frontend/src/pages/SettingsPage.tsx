import { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Switch, Select, Divider, message } from 'antd';
import { UserOutlined, LockOutlined, BellOutlined, GlobalOutlined, ShopOutlined } from '@ant-design/icons';
import { NavBar } from '../components/navbar';
import { Aside } from '../components/aside';
import authService from '../services/authService';
import storeService, { Store } from '../services/storeService';

const SettingsPage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const isAdmin = user?.is_staff || user?.is_superuser;

  // Store state
  const [store, setStore] = useState<Store | null>(null);
  const [loadingStore, setLoadingStore] = useState(true);
  const [editingStore, setEditingStore] = useState(false);
  const [storeForm] = Form.useForm();

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  useEffect(() => {
    if (isAdmin) {
      loadStore();
    } else {
      setLoadingStore(false);
    }
  }, [isAdmin]);

  const loadStore = async () => {
    try {
      setLoadingStore(true);
      const storeData = await storeService.getMyStore();
      setStore(storeData);
      storeForm.setFieldsValue({
        name: storeData.name,
        description: storeData.description || '',
        email: storeData.email || '',
        phone: storeData.phone || '',
        address: storeData.address || '',
      });
    } catch (err: any) {
      if (err.response?.status === 404) {
        // User doesn't have a store yet
        setStore(null);
        setEditingStore(true);
      } else {
        message.error('Erro ao carregar loja');
        console.error(err);
      }
    } finally {
      setLoadingStore(false);
    }
  };

  const handleSaveStore = async (values: any) => {
    try {
      if (store) {
        // Update existing store
        const updatedStore = await storeService.updateStore(store.id, values);
        setStore(updatedStore);
        message.success('Loja atualizada com sucesso!');
        setEditingStore(false);
      } else {
        // Create new store
        const newStore = await storeService.createStore(values);
        setStore(newStore);
        message.success('Loja criada com sucesso!');
        setEditingStore(false);
      }
    } catch (err: any) {
      message.error(err.response?.data?.error || err.response?.data?.name?.[0] || 'Erro ao salvar loja');
      console.error(err);
    }
  };

  const handleCancelStore = () => {
    if (store) {
      storeForm.setFieldsValue({
        name: store.name,
        description: store.description || '',
        email: store.email || '',
        phone: store.phone || '',
        address: store.address || '',
      });
      setEditingStore(false);
    }
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
            {/* Minha Loja - Only for Admins */}
            {isAdmin && (
              <Card
                title={
                  <span className="flex items-center gap-2">
                    <ShopOutlined />
                    Minha Loja
                  </span>
                }
                className="mb-6"
                loading={loadingStore}
                extra={
                  store && !editingStore && (
                    <Button type="primary" onClick={() => setEditingStore(true)}>
                      Editar
                    </Button>
                  )
                }
              >
                {!store && !editingStore && !loadingStore && (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">
                      Você ainda não tem uma loja. Crie uma para começar a adicionar produtos!
                    </p>
                    <Button type="primary" onClick={() => setEditingStore(true)}>
                      Criar Loja
                    </Button>
                  </div>
                )}

                {(editingStore || (!store && !loadingStore)) && (
                  <Form form={storeForm} layout="vertical" onFinish={handleSaveStore}>
                    <Form.Item
                      label="Nome da Loja"
                      name="name"
                      rules={[{ required: true, message: 'Por favor, insira o nome da loja' }]}
                    >
                      <Input placeholder="Ex: Minha Loja" />
                    </Form.Item>
                    <Form.Item label="Descrição" name="description">
                      <Input.TextArea rows={3} placeholder="Descreva sua loja..." />
                    </Form.Item>
                    <Form.Item label="Email" name="email">
                      <Input type="email" placeholder="loja@exemplo.com" />
                    </Form.Item>
                    <Form.Item label="Telefone" name="phone">
                      <Input placeholder="(11) 99999-9999" />
                    </Form.Item>
                    <Form.Item label="Endereço" name="address">
                      <Input.TextArea rows={2} placeholder="Rua, número, bairro, cidade, estado" />
                    </Form.Item>
                    <Form.Item>
                      <div className="flex gap-3">
                        <Button type="primary" htmlType="submit">
                          {store ? 'Atualizar Loja' : 'Criar Loja'}
                        </Button>
                        {store && (
                          <Button onClick={handleCancelStore}>
                            Cancelar
                          </Button>
                        )}
                      </div>
                    </Form.Item>
                  </Form>
                )}

                {store && !editingStore && !loadingStore && (
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm text-gray-500">Nome</div>
                      <div className="text-base font-medium">{store.name}</div>
                    </div>
                    {store.description && (
                      <div>
                        <div className="text-sm text-gray-500">Descrição</div>
                        <div className="text-base">{store.description}</div>
                      </div>
                    )}
                    {store.email && (
                      <div>
                        <div className="text-sm text-gray-500">Email</div>
                        <div className="text-base">{store.email}</div>
                      </div>
                    )}
                    {store.phone && (
                      <div>
                        <div className="text-sm text-gray-500">Telefone</div>
                        <div className="text-base">{store.phone}</div>
                      </div>
                    )}
                    {store.address && (
                      <div>
                        <div className="text-sm text-gray-500">Endereço</div>
                        <div className="text-base">{store.address}</div>
                      </div>
                    )}
                    <div>
                      <div className="text-sm text-gray-500">Status</div>
                      <div className="text-base">
                        {store.is_active ? (
                          <span className="text-green-600">Ativa</span>
                        ) : (
                          <span className="text-red-600">Inativa</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            )}

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