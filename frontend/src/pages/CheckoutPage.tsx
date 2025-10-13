import React, { useState } from 'react';
import { Input, Button, List, Space, InputNumber, message } from 'antd';
import ApiErrorAlert from '../components/common/ApiErrorAlert';
import orderService from '../services/orderService';
import { useCart } from '../context/CartContext';
import { useNavigate } from 'react-router-dom';

const CheckoutPage: React.FC = () => {
  const [error, setError] = useState<any>(null);
  const [email, setEmail] = useState('cliente@example.com');
  const { state, dispatch } = useCart();
  const navigate = useNavigate();

  const handlePlaceOrder = async () => {
    setError(null);
    // build payload from cart
  const items = state.items.map((i: any) => ({ product: i.productId, variant: i.variantId || null, quantity: i.quantity }));
    const payload = {
      customer_name: 'Cliente Teste',
      customer_email: email,
      customer_phone: '123456789',
      shipping_address: 'Rua Teste, 123',
      status: 'pending',
      items,
    };

    try {
      const res = await orderService.createOrder(payload);
      // success: clear cart and redirect
      dispatch({ type: 'CLEAR_CART' });
      message.success('Pedido criado: ' + res.id);
      navigate('/sales');
    } catch (err) {
      setError(err);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Checkout</h1>
      <ApiErrorAlert error={error} />

      <List
        dataSource={state.items}
        bordered
        locale={{ emptyText: 'Seu carrinho está vazio' }}
        renderItem={(item: any) => {
          const product = item.product;
          const variant = product?.variants?.find((v: any) => v.id === item.variantId) ?? null;
          const unitPrice = variant ? Number(variant.price) : product ? Number(product.price) : 0;

          return (
            <List.Item
              actions={[
                <InputNumber
                  min={1}
                  value={item.quantity}
                  onChange={(val: number | null) => dispatch({ type: 'SET_QUANTITY', payload: { productId: item.productId, variantId: item.variantId, quantity: Number(val ?? 1) } })}
                />,
                <Button danger onClick={() => dispatch({ type: 'REMOVE_ITEM', payload: { productId: item.productId, variantId: item.variantId } })}>Remove</Button>
              ]}
            >
              <Space direction="horizontal" align="center">
                {product?.image ? (
                  <img src={product.image} alt={product.name} style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 8 }} />
                ) : (
                  <div style={{ width: 80, height: 80, background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 8 }}>📦</div>
                )}

                <div>
                  <div style={{ fontWeight: 600 }}>{product?.name ?? `Produto ${item.productId}`}</div>
                  {variant && (
                    <div style={{ fontSize: 12, color: '#666' }}>Variante: {variant.size || ''} {variant.color ? `• ${variant.color}` : ''} • SKU: {variant.sku}</div>
                  )}
                  <div style={{ marginTop: 6, fontWeight: 700 }}>R$ {unitPrice.toFixed(2)}</div>
                  <div style={{ fontSize: 12, color: '#666' }}>Quantidade: {item.quantity}</div>
                </div>
              </Space>
            </List.Item>
          );
        }}
      />

      <div className="mt-4 mb-4">
        <label className="block mb-2">Email</label>
        <Input value={email} onChange={(e) => setEmail(e.target.value)} />
      </div>

      <Button type="primary" onClick={handlePlaceOrder} disabled={state.items.length === 0}>Place Order</Button>
    </div>
  );
};

export default CheckoutPage;
