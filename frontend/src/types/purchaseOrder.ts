// Novo arquivo: frontend/src/types/purchaseOrder.ts

import { ProductVariant, Product } from "./product"; // CORREÇÃO 1: Importa Product

export type Supplier = {
  id: number;
  name: string;
  contact_name: string;
  email: string;
  phone: string;
  address: string;
  store: number;
};

export type PurchaseOrderItem = {
  id: number;
  purchase_order: number;
  variant: number; // ID da ProductVariant
  ordered_quantity: number;
  received_quantity: number;
  unit_cost: number;

  // Campos lidos (Read-only)
  variant_name: string;
  product_name: string;
  sku: string;
  total_cost: number;
};

// Tipo extendido da Variante para a página PO, para ter o objeto Product aninhado
// (Necessário para a seleção de variantes no modal de criação)
export type ExtendedProductVariant = ProductVariant & {
  product: Pick<Product, "name" | "store">;
};

export type PurchaseOrder = {
  id: number;
  store: number;
  supplier: number;
  supplier_name: string; // Campo Read-only
  status:
    | "DRAFT"
    | "PENDING"
    | "ORDERED"
    | "RECEIVED_PARTIAL"
    | "RECEIVED_FULL"
    | "CANCELLED";
  order_date: string; // ISO string
  expected_delivery_date: string | null;
  total_cost: number;
  notes: string;

  // Itens (Nested)
  po_items: PurchaseOrderItem[];
};

// CORREÇÃO 2: Ajuste no tipo de payload para criação de PO.
// O tipo original excluía 'store' incorretamente; a View do Django requer 'store' ou o ViewSet o infere.
// Como o ViewSet infere, mas o frontend pode precisar enviar a ID para validação inicial,
// vou permitir 'store' como campo a ser enviado.
export type PurchaseOrderCreatePayload = Omit<
  PurchaseOrder,
  "id" | "order_date" | "total_cost" | "po_items" | "supplier_name"
> & {
  po_items: Omit<
    PurchaseOrderItem,
    | "id"
    | "purchase_order"
    | "variant_name"
    | "product_name"
    | "sku"
    | "total_cost"
  >[];
};
