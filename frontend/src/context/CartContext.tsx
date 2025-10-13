import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Product } from '../types/product';

export interface CartItem {
  productId: number;
  variantId?: number | null;
  quantity: number;
  product?: Product;
  // optional snapshot of the variant chosen at add-to-cart time
  variantSnapshot?: {
    id?: number | null;
    sku?: string | null;
    price?: string | number | null;
    color?: string | null;
    size?: string | null;
    image?: string | null;
  } | null;
}

type State = {
  items: CartItem[];
};

type Action =
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'REMOVE_ITEM'; payload: { productId: number; variantId?: number | null } }
  | { type: 'SET_QUANTITY'; payload: { productId: number; variantId?: number | null; quantity: number } }
  | { type: 'CLEAR_CART' };

const STORAGE_KEY = 'cart_v1';

function loadInitialState(): State {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as State;
  } catch (e) {
    // ignore
  }
  return { items: [] };
}

const initialState: State = loadInitialState();

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'ADD_ITEM': {
      const items = [...state.items];
      const existingIndex = items.findIndex(i => i.productId === action.payload.productId && i.variantId === action.payload.variantId);
      if (existingIndex >= 0) {
        const existing = items[existingIndex];
        if (existing) {
          items[existingIndex] = { ...existing, quantity: existing.quantity + action.payload.quantity };
          return { ...state, items };
        }
      }
      // add new item (payload may include product and variantSnapshot)
      return { ...state, items: [...items, action.payload] };
    }
    case 'REMOVE_ITEM': {
      return { ...state, items: state.items.filter(i => !(i.productId === action.payload.productId && i.variantId === action.payload.variantId)) };
    }
    case 'SET_QUANTITY': {
      const items = state.items.map(i => {
        if (i.productId === action.payload.productId && i.variantId === action.payload.variantId) {
          return { ...i, quantity: action.payload.quantity };
        }
        return i;
      }).filter(i => i.quantity > 0);
      return { ...state, items };
    }
    case 'CLEAR_CART':
      return { ...state, items: [] };
    default:
      return state;
  }
}

const CartContext = createContext<{
  state: State;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export const CartProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  // persist
  React.useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // ignore
    }
  }, [state]);
  return <CartContext.Provider value={{ state, dispatch }}>{children}</CartContext.Provider>;
};

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used within CartProvider');
  return ctx;
}
