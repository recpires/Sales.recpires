import { FC, useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();
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
        label={t('product_form.name_label')}
        name="name"
        rules={[{ required: true, message: t('product_form.name_required') }]}
      >
        <Input placeholder={t('product_form.name_placeholder')} />
      </Form.Item>

      <Form.Item
        label={t('product_form.description_label')}
        name="description"
      >
        <TextArea rows={3} placeholder={t('product_form.description_placeholder')} />
      </Form.Item>

      <div className="grid grid-cols-2 gap-4">
        <Form.Item
          label={t('product_form.price_label')}
          name="price"
          rules={[{ required: true, message: t('product_form.price_required') }]}
        >
          <InputNumber
            min={0.01}
            step={0.01}
            precision={2}
            className="w-full"
            placeholder={t('product_form.price_placeholder')}
          />
        </Form.Item>

        <Form.Item
          label={t('product_form.stock_label')}
          name="stock"
          rules={[{ required: true, message: t('product_form.stock_required') }]}
        >
          <InputNumber min={0} className="w-full" placeholder={t('product_form.stock_placeholder')} />
        </Form.Item>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Form.Item
          label={t('product_form.color_label')}
          name="color"
          rules={[{ required: true, message: t('product_form.color_required') }]}
        >
          <Select options={colorOptions} placeholder={t('product_form.color_placeholder')} />
        </Form.Item>

        <Form.Item
          label={t('product_form.size_label')}
          name="size"
          rules={[{ required: true, message: t('product_form.size_required') }]}
        >
          <Select options={sizeOptions} placeholder={t('product_form.size_placeholder')} />
        </Form.Item>
      </div>

      <Form.Item
        label={t('product_form.sku_label')}
        name="sku"
        rules={[{ required: true, message: t('product_form.sku_required') }]}
      >
        <Input placeholder={t('product_form.sku_placeholder')} />
      </Form.Item>

      <Form.Item
        label={t('product_form.image_label')}
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
              <div style={{ marginTop: 8 }}>{t('product_form.upload_button')}</div>
            </div>
          )}
        </Upload>
      </Form.Item>

      <Form.Item
        label={t('product_form.active_label')}
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
