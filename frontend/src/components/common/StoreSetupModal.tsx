import { FC, useEffect } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { ShopOutlined } from '@ant-design/icons';
import { useCreateStore, useUpdateStore } from '../../hooks/useStore';
import { StoreCreateData, StoreUpdateData } from '../../services/storeService';
import { Store } from '../../types/store';

const { TextArea } = Input;

interface StoreSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  store?: Store | null; // Optional existing store data for edit mode
}

export const StoreSetupModal: FC<StoreSetupModalProps> = ({ isOpen, onClose, onSuccess, store }) => {
  const [form] = Form.useForm();
  const createStoreMutation = useCreateStore();
  const updateStoreMutation = useUpdateStore();

  const isEditMode = !!store;

  // Initialize form with existing store data when modal opens in edit mode
  useEffect(() => {
    if (isOpen && store) {
      form.setFieldsValue({
        name: store.name,
        description: store.description,
        phone: store.phone,
        email: store.email,
        address: store.address,
      });
    } else if (isOpen && !store) {
      form.resetFields();
    }
  }, [isOpen, store, form]);

  const handleSubmit = async (values: StoreCreateData) => {
    try {
      if (isEditMode && store) {
        // Update existing store
        await updateStoreMutation.mutateAsync({ id: store.id, data: values as StoreUpdateData });
        message.success('Loja atualizada com sucesso!');
      } else {
        // Create new store
        await createStoreMutation.mutateAsync(values);
        message.success('Loja criada com sucesso!');
      }
      form.resetFields();
      onSuccess?.();
      onClose();
    } catch (error: any) {
      const errorMessage = isEditMode
        ? 'Erro ao atualizar loja'
        : 'Erro ao criar loja';
      message.error(error.response?.data?.detail || errorMessage);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title={
        <div className="flex items-center gap-2">
          <ShopOutlined className="text-2xl text-blue-500" />
          <span>{isEditMode ? 'Editar Loja' : 'Configure sua Loja'}</span>
        </div>
      }
      open={isOpen}
      onCancel={handleCancel}
      footer={null}
      width={600}
      closable={true}
      maskClosable={false}
    >
      <div className="mb-4">
        <p className="text-gray-600">
          {isEditMode
            ? 'Atualize as informações da sua loja:'
            : 'Para começar a vender, você precisa configurar sua loja primeiro. Preencha as informações abaixo:'}
        </p>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          label="Nome da Loja"
          name="name"
          rules={[{ required: true, message: 'Por favor, insira o nome da loja' }]}
        >
          <Input placeholder="Ex: Minha Loja de Roupas" size="large" />
        </Form.Item>

        <Form.Item
          label="Descrição"
          name="description"
        >
          <TextArea
            rows={3}
            placeholder="Descreva sua loja e o que você vende..."
            size="large"
          />
        </Form.Item>

        <div className="grid grid-cols-2 gap-4">
          <Form.Item
            label="Telefone"
            name="phone"
          >
            <Input placeholder="(11) 99999-9999" size="large" />
          </Form.Item>

          <Form.Item
            label="E-mail"
            name="email"
          >
            <Input type="email" placeholder="contato@minhaloja.com" size="large" />
          </Form.Item>
        </div>

        <Form.Item
          label="Endereço"
          name="address"
        >
          <TextArea
            rows={2}
            placeholder="Rua, número, bairro, cidade - UF"
            size="large"
          />
        </Form.Item>

        <Form.Item className="mb-0">
          <Button
            type="primary"
            htmlType="submit"
            loading={createStoreMutation.isPending || updateStoreMutation.isPending}
            block
            size="large"
          >
            {isEditMode ? 'Atualizar Loja' : 'Criar Loja'}
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};
