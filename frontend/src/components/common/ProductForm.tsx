import { FC, useState } from 'react';
import { Form, Input, InputNumber, Select, Switch, Upload, Button, message } from 'antd';
import { UploadOutlined, PlusOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { ColorChoice, SizeChoice } from '../../types/product';

const { TextArea } = Input;

interface ProductFormData {
  name: string;
  description: string;
  price: number;
  color: ColorChoice;
  size: SizeChoice;
  stock: number;
  sku: string;
  is_active: boolean;
}

interface ProductFormProps {
  onSubmit: (data: ProductFormData, image?: File) => Promise<void>;
  initialValues?: Partial<ProductFormData>;
  submitText?: string;
  loading?: boolean;
}

const colorOptions = [
  { value: 'red', label: 'Vermelho' },
  { value: 'blue', label: 'Azul' },
  { value: 'green', label: 'Verde' },
  { value: 'black', label: 'Preto' },
  { value: 'white', label: 'Branco' },
  { value: 'yellow', label: 'Amarelo' },
  { value: 'pink', label: 'Rosa' },
  { value: 'purple', label: 'Roxo' },
  { value: 'orange', label: 'Laranja' },
  { value: 'gray', label: 'Cinza' },
];

const sizeOptions = [
  { value: 'XS', label: 'Extra Pequeno (XS)' },
  { value: 'S', label: 'Pequeno (S)' },
  { value: 'M', label: 'Médio (M)' },
  { value: 'L', label: 'Grande (L)' },
  { value: 'XL', label: 'Extra Grande (XL)' },
  { value: 'XXL', label: 'Extra Extra Grande (XXL)' },
];

export const ProductForm: FC<ProductFormProps> = ({
  onSubmit,
  initialValues,
  submitText = 'Criar Produto',
  loading = false,
}) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [imageFile, setImageFile] = useState<File | undefined>();

  const handleUploadChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);
    if (newFileList.length > 0 && newFileList[0].originFileObj) {
      setImageFile(newFileList[0].originFileObj);
    } else {
      setImageFile(undefined);
    }
  };

  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('Você só pode fazer upload de arquivos de imagem!');
      return Upload.LIST_IGNORE;
    }

    const isLt5M = file.size / 1024 / 1024 < 5;
    if (!isLt5M) {
      message.error('A imagem deve ter menos de 5MB!');
      return Upload.LIST_IGNORE;
    }

    return false; // Prevent auto upload
  };

  const handleFinish = async (values: ProductFormData) => {
    try {
      await onSubmit(values, imageFile);
      form.resetFields();
      setFileList([]);
      setImageFile(undefined);
    } catch (error) {
      console.error('Erro ao submeter formulário:', error);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleFinish}
      initialValues={{
        is_active: true,
        color: 'black',
        size: 'M',
        stock: 0,
        ...initialValues,
      }}
    >
      <Form.Item
        label="Nome do Produto"
        name="name"
        rules={[{ required: true, message: 'Por favor, insira o nome do produto!' }]}
      >
        <Input placeholder="Ex: Camiseta Básica" />
      </Form.Item>

      <Form.Item
        label="Descrição"
        name="description"
      >
        <TextArea rows={3} placeholder="Descrição detalhada do produto" />
      </Form.Item>

      <div className="grid grid-cols-2 gap-4">
        <Form.Item
          label="Preço (R$)"
          name="price"
          rules={[{ required: true, message: 'Por favor, insira o preço!' }]}
        >
          <InputNumber
            min={0.01}
            step={0.01}
            precision={2}
            className="w-full"
            placeholder="0.00"
          />
        </Form.Item>

        <Form.Item
          label="Estoque"
          name="stock"
          rules={[{ required: true, message: 'Por favor, insira a quantidade em estoque!' }]}
        >
          <InputNumber min={0} className="w-full" placeholder="0" />
        </Form.Item>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Form.Item
          label="Cor"
          name="color"
          rules={[{ required: true, message: 'Por favor, selecione a cor!' }]}
        >
          <Select options={colorOptions} placeholder="Selecione a cor" />
        </Form.Item>

        <Form.Item
          label="Tamanho"
          name="size"
          rules={[{ required: true, message: 'Por favor, selecione o tamanho!' }]}
        >
          <Select options={sizeOptions} placeholder="Selecione o tamanho" />
        </Form.Item>
      </div>

      <Form.Item
        label="SKU"
        name="sku"
        rules={[{ required: true, message: 'Por favor, insira o SKU!' }]}
      >
        <Input placeholder="Ex: PROD-001" />
      </Form.Item>

      <Form.Item
        label="Imagem do Produto"
        name="image"
      >
        <Upload
          listType="picture-card"
          fileList={fileList}
          onChange={handleUploadChange}
          beforeUpload={beforeUpload}
          maxCount={1}
        >
          {fileList.length === 0 && (
            <div>
              <PlusOutlined />
              <div style={{ marginTop: 8 }}>Upload</div>
            </div>
          )}
        </Upload>
      </Form.Item>

      <Form.Item
        label="Produto Ativo"
        name="is_active"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block size="large">
          {submitText}
        </Button>
      </Form.Item>
    </Form>
  );
};

export default ProductForm;
