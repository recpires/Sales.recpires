import React from 'react';
import { render, screen } from '@testing-library/react';
import CheckoutPage from '../pages/CheckoutPage';
import { CartProvider } from '../context/CartContext';

describe('CheckoutPage', () => {
  it('shows empty cart message', () => {
    render(
      <CartProvider>
        <CheckoutPage />
      </CartProvider>
    );

    expect(screen.getByText(/Seu carrinho está vazio/i)).toBeTruthy();
  });
});
