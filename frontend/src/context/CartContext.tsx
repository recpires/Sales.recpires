import React, { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import { Product } from '../types/product';

interface CartItem {
  productId: number;
  variantId: number | null;
  quantity: number;
  price: number;
  product: Product;
  variantSnapshot: any | null;
}

interface CartState {
  items: CartItem[];
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: { productId: number; variantId: number | null; quantity: number; product: Product; variantSnapshot: any | null } }
  | { type: 'REMOVE_ITEM'; payload: { productId: number; variantId: number | null } }
  | { type: 'UPDATE_QUANTITY'; payload: { productId: number; variantId: number | null; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_CART'; payload: CartItem[] };

const CartContext = createContext<{
  state: CartState;
  dispatch: React.Dispatch<CartAction>;
} | undefined>(undefined);

const CART_STORAGE_KEY = 'shopping_cart';

const loadCartFromStorage = (): CartItem[] => {
  try {
    const stored = localStorage.getItem(CART_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error loading cart from storage:', error);
  }
  return [];
};

const saveCartToStorage = (items: CartItem[]) => {
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
  } catch (error) {
    console.error('Error saving cart to storage:', error);
  }
};

const cartReducer = (state: CartState, action: CartAction): CartState => {
  let newState: CartState;

  switch (action.type) {
    case 'ADD_ITEM': {
      const { productId, variantId, quantity, product, variantSnapshot } = action.payload;
      const existingItemIndex = state.items.findIndex(
        (item) => item.productId === productId && item.variantId === variantId
      );

      if (existingItemIndex > -1) {
        const newItems = [...state.items];
        newItems[existingItemIndex].quantity += quantity;
        newState = { ...state, items: newItems };
      } else {
        // Get price from variant snapshot, first variant, or product
        const firstVariant =
          Array.isArray(product.variants) && product.variants.length > 0
            ? product.variants[0]
            : null;
        const price = variantSnapshot?.price ?? firstVariant?.price ?? product.price ?? 0;

        newState = {
          ...state,
          items: [
            ...state.items,
            {
              productId,
              variantId: variantId ?? null,
              quantity,
              price,
              product,
              variantSnapshot: variantSnapshot ?? null,
            },
          ],
        };
      }
      saveCartToStorage(newState.items);
      return newState;
    }

    case 'REMOVE_ITEM': {
      const { productId, variantId } = action.payload;
      newState = {
        ...state,
        items: state.items.filter(
          (item) => !(item.productId === productId && item.variantId === variantId)
        ),
      };
      saveCartToStorage(newState.items);
      return newState;
    }

    case 'UPDATE_QUANTITY': {
      const { productId, variantId, quantity } = action.payload;
      if (quantity <= 0) {
        newState = {
          ...state,
          items: state.items.filter(
            (item) => !(item.productId === productId && item.variantId === variantId)
          ),
        };
      } else {
        newState = {
          ...state,
          items: state.items.map((item) =>
            item.productId === productId && item.variantId === variantId
              ? { ...item, quantity }
              : item
          ),
        };
      }
      saveCartToStorage(newState.items);
      return newState;
    }

    case 'CLEAR_CART':
      saveCartToStorage([]);
      return { ...state, items: [] };

    case 'LOAD_CART':
      return { ...state, items: action.payload };

    default:
      return state;
  }
};

export const CartProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, { items: [] });

  useEffect(() => {
    const savedCart = loadCartFromStorage();
    if (savedCart.length > 0) {
      dispatch({ type: 'LOAD_CART', payload: savedCart });
    }
  }, []);

  return <CartContext.Provider value={{ state, dispatch }}>{children}</CartContext.Provider>;
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
