import React, { createContext, useContext, useReducer, ReactNode } from "react";
// Certifique-se que estes tipos refletem a estrutura do backend
import { Product, ProductVariant } from "../types/product";

// --- INTERFACE (sem mudanças) ---
interface CartItem {
  productId: number;
  variantId: number | null;
  quantity: number;
  product: Product;
}

interface CartState {
  items: CartItem[];
}

// --- ACTIONS (Tipo do payload LOAD_CART ajustado) ---
type CartAction =
  | {
      type: "ADD_ITEM";
      payload: {
        productId: number;
        variantId: number | null;
        quantity: number;
        product: Product;
      };
    }
  | {
      type: "REMOVE_ITEM";
      payload: { productId: number; variantId: number | null };
    }
  | {
      type: "UPDATE_QUANTITY";
      payload: {
        productId: number;
        variantId: number | null;
        quantity: number;
      };
    }
  | { type: "CLEAR_CART" }
  | { type: "LOAD_CART"; payload: any[] }; // Tipado como any[] para limpeza no reducer

// --- CONTEXTO (sem mudanças) ---
const CartContext = createContext<
  | {
      state: CartState;
      dispatch: React.Dispatch<CartAction>;
      getTotal: () => number;
    }
  | undefined
>(undefined);

// --- STORAGE (sem mudanças) ---
const CART_STORAGE_KEY = "shopping_cart_v2";

// Retorna any[] para limpeza no reducer
const loadCartFromStorage = (): any[] => {
  try {
    const stored = localStorage.getItem(CART_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error("Error loading cart from storage:", error);
  }
  return [];
};

const saveCartToStorage = (items: CartItem[]) => {
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
  } catch (error) {
    console.error("Error saving cart to storage:", error);
  }
};

// --- REDUCER CORRIGIDO ---
const cartReducer = (state: CartState, action: CartAction): CartState => {
  let newState: CartState;

  switch (action.type) {
    case "ADD_ITEM": {
      const { productId, variantId, quantity, product } = action.payload;

      // Validação inicial: produto existe e tem variantes?
      if (!product || !Array.isArray(product.variants)) {
        console.error(`Produto inválido ou sem variantes: ID ${productId}`);
        return state;
      }

      // Encontra a variante específica ANTES de mais nada
      const variant = product.variants.find(
        (v: ProductVariant) => v.id === variantId
      ); // Type 'v' explicitly

      // Sai imediatamente se a variante não for encontrada
      if (!variant) {
        console.error(
          `Variante ${variantId} não encontrada no produto ${productId}`
        );
        return state;
      }
      // Agora TS sabe que 'variant' existe; normalize stock para número (0 quando ausente)
      const availableStock = Number(variant.stock ?? 0);

      const existingItemIndex = state.items.findIndex(
        (item) => item.productId === productId && item.variantId === variantId
      );

      if (existingItemIndex > -1) {
        // Item existente
        const currentItem = state.items[existingItemIndex]!; // Non-null assertion
        const currentQuantity = currentItem.quantity;
        const potentialNewQuantity = currentQuantity + quantity;
        const finalQuantity = Math.min(potentialNewQuantity, availableStock);

        if (potentialNewQuantity > availableStock) {
          console.warn(
            `Estoque limitado para ${variant.sku}. Adicionado até o limite de ${availableStock}.`
          );
          // Notificação UI
        }
        if (finalQuantity === currentQuantity) return state; // Sem mudanças

        const newItems = [...state.items];
        // Cria um novo objeto completo para garantir a tipagem correta
        newItems[existingItemIndex] = {
          ...(currentItem as CartItem), // Espalha o item existente (que é CartItem)
          quantity: finalQuantity, // Sobrescreve apenas a quantidade
        };
        newState = { ...state, items: newItems };
      } else {
        // Novo item
        const initialQuantity = Math.min(quantity, availableStock);

        if (initialQuantity <= 0) {
          console.warn(
            `Estoque zerado ou insuficiente para ${variant.sku}. Item não adicionado.`
          );
          return state;
        }
        if (quantity > availableStock) {
          console.warn(
            `Estoque limitado para ${variant.sku}. Adicionando apenas ${availableStock}.`
          );
          // Notificação UI
        }

        // Cria o novo item garantindo todos os campos
        const newItem: CartItem = {
          productId,
          variantId,
          quantity: initialQuantity,
          product,
        };
        newState = { ...state, items: [...state.items, newItem] };
      }
      saveCartToStorage(newState.items);
      return newState;
    }

    case "REMOVE_ITEM": {
      // (Lógica sem erros reportados)
      const { productId, variantId } = action.payload;
      newState = {
        ...state,
        items: state.items.filter(
          (item) =>
            !(item.productId === productId && item.variantId === variantId)
        ),
      };
      saveCartToStorage(newState.items);
      return newState;
    }

    case "UPDATE_QUANTITY": {
      const { productId, variantId, quantity } = action.payload;

      const itemIndex = state.items.findIndex(
        (item) => item.productId === productId && item.variantId === variantId
      );
      if (itemIndex === -1) return state;

      const currentItem = state.items[itemIndex]!; // Non-null assertion
      // CORREÇÃO: Acessa product de currentItem que sabemos existir
      const product = currentItem.product;

      // Validação: product e variants existem?
      if (!product || !Array.isArray(product.variants)) {
        console.error(
          `Produto inválido no item ${productId}/${variantId} durante update.`
        );
        return state; // Ou remove o item?
      }

      const variant = product.variants.find(
        (v: ProductVariant) => v.id === variantId
      ); // Type 'v' explicitly

      // CORREÇÃO: Checa se variant existe *antes* de usar .stock
      if (!variant) {
        console.error(
          `Variante ${variantId} não encontrada no produto ${productId} durante update.`
        );
        return state; // Ou remove o item?
      }
      const availableStock = Number(variant.stock ?? 0);

      if (quantity <= 0) {
        newState = {
          ...state,
          items: state.items.filter((_, index) => index !== itemIndex),
        };
      } else {
        const finalQuantity = Math.min(quantity, availableStock);

        if (quantity > availableStock) {
          console.warn(
            `Estoque limitado para ${variant.sku}. Quantidade ajustada para ${availableStock}.`
          );
          // Notificação UI
        }
        if (finalQuantity === currentItem.quantity) return state; // Sem mudanças

        const newItems = [...state.items];
        // Cria um novo objeto completo para garantir a tipagem correta
        newItems[itemIndex] = {
          ...(currentItem as CartItem), // Espalha o item existente (que é CartItem)
          quantity: finalQuantity, // Sobrescreve apenas a quantidade
        };
        newState = { ...state, items: newItems };
      }

      saveCartToStorage(newState.items);
      return newState;
    }

    case "CLEAR_CART":
      // (Lógica sem erros reportados)
      saveCartToStorage([]);
      return { ...state, items: [] };

    case "LOAD_CART":
      // Mapeia de any[] para CartItem[], removendo 'price' se existir
      const loadedItems: CartItem[] = action.payload
        .map((item: any) => {
          const { price, ...rest } = item; // Tenta remover 'price'
          // Validação básica: item carregado tem os campos mínimos?
          if (
            rest &&
            typeof rest.productId === "number" &&
            (typeof rest.variantId === "number" || rest.variantId === null) &&
            typeof rest.quantity === "number" &&
            rest.product
          ) {
            // Remove campos extras ou inválidos se necessário
            const cleanItem: CartItem = {
              productId: rest.productId,
              // variantId pode ser número ou null (manter o null se estiver salvo assim)
              variantId: rest.variantId,
              quantity: rest.quantity,
              product: rest.product, // Assume que 'product' está no formato correto
            };
            return cleanItem;
          }
          console.warn("Item inválido encontrado no localStorage:", item);
          return null; // Descarta item inválido
        })
        .filter((item): item is CartItem => item !== null); // Remove nulos e garante a tipagem

      return { ...state, items: loadedItems };

    default:
      // Exhaustiveness check: garante que todas as ações foram tratadas.
      // A variável é referenciada com `void` para evitar warning de variável não utilizada.
      const _exhaustiveCheck: never = action;
      void _exhaustiveCheck;
      return state;
  }
};

// --- PROVIDER (sem mudanças significativas) ---
export const CartProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(cartReducer, {
    items: loadCartFromStorage(),
  });

  const getTotal = (): number => {
    return state.items.reduce((total, item) => {
      // CORREÇÃO: Garante que product e variants existem antes do find
      const variant = item.product?.variants?.find(
        (v: ProductVariant) => v.id === item.variantId
      ); // Type 'v' explicitly
      const itemPrice = variant ? Number(variant.price) : 0;
      const quantity =
        Number.isFinite(item.quantity) && item.quantity > 0 ? item.quantity : 0;
      return total + itemPrice * quantity;
    }, 0);
  };

  return (
    <CartContext.Provider value={{ state, dispatch, getTotal }}>
      {children}
    </CartContext.Provider>
  );
};

// --- HOOK (sem mudanças) ---
export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return { ...context, getTotal: context.getTotal };
};
