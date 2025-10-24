import React, { useState } from 'react';
import { Form, Input, InputNumber, Button, Upload, Switch, message } from 'antd';
import { UploadOutlined, PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';

interface ProductFormProps {
  onSubmit: (data: ProductFormData, image?: File) => Promise<void>;
  initialData?: Partial<ProductFormData>;
  submitText?: string;
  loading?: boolean;
}

interface ProductFormData {
  name: string;
  description: string;
  sku: string;
  price?: number;
  stock?: number;
  category: string;
  variants?: Array<{
    name: string;
    sku: string;
    price: number;
    stock: number;
  }>;
}

const ProductForm: React.FC<ProductFormProps> = ({
  onSubmit,
  initialData,
  submitText = 'Salvar',
  loading = false,
}) => {
  const [form] = Form.useForm();
  const [imageFile, setImageFile] = useState<File | undefined>(undefined);
  const [imagePreview, setImagePreview] = useState<string | undefined>(initialData?.image);
  const [useVariants, setUseVariants] = useState(
    Array.isArray(initialData?.variants) && initialData.variants.length > 0
  );

  const handleImageChange = (info: any) => {
    if (info.file.originFileObj) {
      const file = info.file.originFileObj;
      setImageFile(file);

      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (values: ProductFormData) => {
    try {
      // If using variants, remove product-level price/stock
      const submitData = useVariants
        ? { ...values, price: undefined, stock: undefined }
        : { ...values, variants: undefined };

      await onSubmit(submitData, imageFile);
      form.resetFields();
      setImageFile(undefined);
      setImagePreview(undefined);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  const handleUseVariantsChange = (checked: boolean) => {
    setUseVariants(checked);
    if (checked) {
      form.setFieldsValue({ price: undefined, stock: undefined });
    } else {
      form.setFieldsValue({ variants: undefined });
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={initialData}
      className="max-h-[70vh] overflow-y-auto px-2"
    >
      <Form.Item
        label="Nome do Produto"
        name="name"
        rules={[{ required: true, message: 'Por favor, insira o nome do produto' }]}
      >
        <Input placeholder="Ex: Camiseta Básica" size="large" />
      </Form.Item>

      <Form.Item
        label="Descrição"
        name="description"
        rules={[{ required: true, message: 'Por favor, insira a descrição' }]}
      >
        <Input.TextArea
          placeholder="Descreva o produto..."
          rows={3}
          showCount
          maxLength={500}
        />
      </Form.Item>

      <Form.Item
        label="SKU (Código único)"
        name="sku"
        rules={[
          { required: true, message: 'Por favor, insira o SKU' },
          { pattern: /^[A-Za-z0-9-_]+$/, message: 'SKU deve conter apenas letras, números, - ou _' },
        ]}
      >
        <Input placeholder="Ex: CAM-BAS-001" size="large" />
      </Form.Item>

      <Form.Item label="Categoria" name="category">
        <Input placeholder="Ex: Roupas, Eletrônicos, etc." size="large" />
      </Form.Item>

      {/* Toggle Variants */}
      <Form.Item
        label="Usar Variantes"
        tooltip="Produtos com variantes (tamanhos, cores, etc.) não têm preço/estoque fixo"
      >
        <Switch checked={useVariants} onChange={handleUseVariantsChange} />
        <span className="ml-2 text-gray-500">
          {useVariants ? 'Produto com variantes' : 'Produto simples'}
        </span>
      </Form.Item>

      {!useVariants ? (
        <>
          <Form.Item
            label="Preço (R$)"
            name="price"
            rules={[{ required: true, message: 'Por favor, insira o preço' }]}
          >
            <InputNumber
              prefix="R$"
              style={{ width: '100%' }}
              min={0}
              precision={2}
              size="large"
              placeholder="0,00"
            />
          </Form.Item>

          <Form.Item
            label="Estoque"
            name="stock"
            rules={[{ required: true, message: 'Por favor, insira a quantidade em estoque' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              size="large"
              placeholder="Quantidade disponível"
            />
          </Form.Item>
        </>
      ) : (
        <Form.List
          name="variants"
          rules={[
            {
              validator: async (_, variants) => {
                if (!variants || variants.length < 1) {
                  return Promise.reject(new Error('Adicione pelo menos uma variante'));
                }
              },
            },
          ]}
        >
          {(fields, { add, remove }, { errors }) => (
            <>
              {fields.map((field, index) => (
                <div key={field.key} className="border border-gray-200 p-4 rounded-lg mb-4 bg-gray-50">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-semibold text-gray-700">Variante {index + 1}</h4>
                    <Button
                      type="text"
                      danger
                      icon={<MinusCircleOutlined />}
                      onClick={() => remove(field.name)}
                    >
                      Remover
                    </Button>
                  </div>

                  <Form.Item
                    {...field}
                    label="Nome da Variante"
                    name={[field.name, 'name']}
                    rules={[{ required: true, message: 'Nome obrigatório' }]}
                  >
                    <Input placeholder="Ex: Tamanho M, Cor Azul" />
                  </Form.Item>

                  <Form.Item
                    {...field}
                    label="SKU da Variante"
                    name={[field.name, 'sku']}
                    rules={[
                      { required: true, message: 'SKU obrigatório' },
                      { pattern: /^[A-Za-z0-9-_]+$/, message: 'SKU inválido' },
                    ]}
                  >
                    <Input placeholder="Ex: CAM-BAS-M-AZ" />
                  </Form.Item>

                  <div className="grid grid-cols-2 gap-4">
                    <Form.Item
                      {...field}
                      label="Preço (R$)"
                      name={[field.name, 'price']}
                      rules={[{ required: true, message: 'Preço obrigatório' }]}
                    >
                      <InputNumber
                        prefix="R$"
                        style={{ width: '100%' }}
                        min={0}
                        precision={2}
                        placeholder="0,00"
                      />
                    </Form.Item>

                    <Form.Item
                      {...field}
                      label="Estoque"
                      name={[field.name, 'stock']}
                      rules={[{ required: true, message: 'Estoque obrigatório' }]}
                    >
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="Quantidade" />
                    </Form.Item>
                  </div>
                </div>
              ))}

              <Form.Item>
                <Button
                  type="dashed"
                  onClick={() => add()}
                  block
                  icon={<PlusOutlined />}
                  size="large"
                >
                  Adicionar Variante
                </Button>
                <Form.ErrorList errors={errors} />
              </Form.Item>
            </>
          )}
        </Form.List>
      )}

      {/* Image Upload */}
      <Form.Item label="Imagem do Produto">
        <Upload
          beforeUpload={() => false}
          onChange={handleImageChange}
          maxCount={1}
          listType="picture-card"
          showUploadList={false}
        >
          {imagePreview ? (
            <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
          ) : (
            <div className="flex flex-col items-center justify-center">
              <UploadOutlined className="text-3xl text-gray-400" />
              <div className="mt-2 text-gray-600">Enviar Imagem</div>
            </div>
          )}
        </Upload>
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
