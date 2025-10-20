import React, { createContext, useContext, useReducer, useEffect, Dispatch } from 'react';

export interface ProductVariant {
  id: number;
  size?: string;
  color?: string;
  sku: string;
  price: string;
  stock: number;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  price: string;
  sku: string;
  stock: number;
  image?: string;
  variants?: ProductVariant[];
}

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  product?: Product;
  variantSnapshot?: any | null;
}

interface CartState {
  items: CartItem[];
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'REMOVE_ITEM'; payload: { productId: number; variantId?: number | null } }
  | { type: 'SET_QUANTITY'; payload: { productId: number; variantId?: number | null; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'SET_CART'; payload: CartItem[] };

interface CartContextType {
  state: CartState;
  dispatch: Dispatch<CartAction>;
  getTotal: () => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

const initialState: CartState = {
  items: [],
};

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingIndex = state.items.findIndex(
        i => i.productId === action.payload.productId && i.variantId === action.payload.variantId
      );
      if (existingIndex >= 0) {
        const items = [...state.items];
        items[existingIndex] = {
          ...items[existingIndex],
          quantity: items[existingIndex].quantity + action.payload.quantity,
        };
        return { ...state, items };
      }
      return { ...state, items: [...state.items, action.payload] };
    }
    case 'REMOVE_ITEM':
      return {
        ...state,
        items: state.items.filter(
          i => !(i.productId === action.payload.productId && i.variantId === action.payload.variantId)
        ),
      };
    case 'SET_QUANTITY': {
      const items = state.items.map(i => {
        if (i.productId === action.payload.productId && i.variantId === action.payload.variantId) {
          return { ...i, quantity: action.payload.quantity };
        }
        return i;
      });
      return { ...state, items };
    }
    case 'REMOVE_ITEM':
      return { ...state, items: state.items.filter(i => i.id !== action.payload.id) };
    case 'CLEAR_CART':
      return { ...state, items: [] };
    case 'SET_CART':
      return { ...state, items: action.payload };
    default:
      return state;
  }
}

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialState, () => {
    try {
      const raw = localStorage.getItem('cart');
      return raw ? { items: JSON.parse(raw) as CartItem[] } : initialState;
    } catch {
      return initialState;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('cart', JSON.stringify(state.items));
    } catch {
      /* ignore storage errors */
    }
  }, [state.items]);

  const getTotal = () => {
    return state.items.reduce((total, item) => {
      const product = item.product;
      if (!product) return total;

      const variant = product.variants?.find(v => v.id === item.variantId);
      const unitPrice = variant ? Number(variant.price) : Number(product.price);

      return total + unitPrice * item.quantity;
    }, 0);
  };

  return (
    <CartContext.Provider value={{ state, dispatch, getTotal }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = (): CartContextType => {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used within CartProvider');
  return ctx;
};
