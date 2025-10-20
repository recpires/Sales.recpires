import { FC } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { ShopOutlined } from '@ant-design/icons';
import { useCreateStore } from '../../hooks/useStore';
import { StoreCreateData } from '../../services/storeService';

const { TextArea } = Input;

interface StoreSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const StoreSetupModal: FC<StoreSetupModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [form] = Form.useForm();
  const createStoreMutation = useCreateStore();

  const handleSubmit = async (values: StoreCreateData) => {
    try {
      await createStoreMutation.mutateAsync(values);
      message.success('Loja criada com sucesso!');
      form.resetFields();
      onSuccess?.();
      onClose();
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Erro ao criar loja');
    }
  };

  return (
    <Modal
      title={
        <div className="flex items-center gap-2">
          <ShopOutlined className="text-2xl text-blue-500" />
          <span>Configure sua Loja</span>
        </div>
      }
      open={isOpen}
      onCancel={onClose}
      footer={null}
      width={600}
      closable={false}
      maskClosable={false}
    >
      <div className="mb-4">
        <p className="text-gray-600">
          Para começar a vender, você precisa configurar sua loja primeiro.
          Preencha as informações abaixo:
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
            loading={createStoreMutation.isPending}
            block
            size="large"
          >
            Criar Loja
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};
