// Novo arquivo: frontend/src/services/purchaseOrderService.ts

import { api } from "./api"; // CORREÇÃO 1: Importação de 'api'
import {
  PurchaseOrder,
  PurchaseOrderCreatePayload,
  Supplier,
} from "../types/purchaseOrder"; // CORREÇÃO 2: Removida importação não utilizada de PurchaseOrderItem
import { formatError } from "./errorUtils"; // CORREÇÃO 3: Importação de 'formatError'

const BASE_URL_SUPPLIERS = "/suppliers";
const BASE_URL_POS = "/purchase-orders";

/**
 * Funções para Fornecedores (Suppliers)
 */
export const getSuppliers = async (storeId: number): Promise<Supplier[]> => {
  try {
    const response = await api.get<Supplier[]>(
      `${BASE_URL_SUPPLIERS}/?store=${storeId}`
    );
    return response.data;
  } catch (error) {
    throw formatError(error);
  }
};

// CORREÇÃO 4: Adicionando o campo `store` ao tipo `supplierData` para o POST
export const createSupplier = async (
  supplierData: Omit<Supplier, "id">
): Promise<Supplier> => {
  try {
    const response = await api.post<Supplier>(
      BASE_URL_SUPPLIERS + "/",
      supplierData
    );
    return response.data;
  } catch (error) {
    throw formatError(error);
  }
};

/**
 * Funções para Pedidos de Compra (Purchase Orders - PO)
 */
export const getPurchaseOrders = async (
  storeId: number
): Promise<PurchaseOrder[]> => {
  try {
    const response = await api.get<PurchaseOrder[]>(
      `${BASE_URL_POS}/?store=${storeId}`
    );
    return response.data;
  } catch (error) {
    throw formatError(error);
  }
};

export const getPurchaseOrder = async (
  poId: number
): Promise<PurchaseOrder> => {
  try {
    const response = await api.get<PurchaseOrder>(`${BASE_URL_POS}/${poId}/`);
    return response.data;
  } catch (error) {
    throw formatError(error);
  }
};

// CORREÇÃO 5: Removendo o Omit<PurchaseOrder, ...> do payload e adicionando 'store'
export const createPurchaseOrder = async (
  poData: PurchaseOrderCreatePayload & { store: number }
): Promise<PurchaseOrder> => {
  try {
    const response = await api.post<PurchaseOrder>(BASE_URL_POS + "/", poData);
    return response.data;
  } catch (error) {
    throw formatError(error);
  }
};

export const updatePurchaseOrder = async (
  poId: number,
  poData: Partial<PurchaseOrderCreatePayload>
): Promise<PurchaseOrder> => {
  try {
    // O `po_items` deve ser tratado separadamente ou com cuidado no backend.
    // Para simplificar a API, passamos o objeto completo do PO.
    const response = await api.patch<PurchaseOrder>(
      `${BASE_URL_POS}/${poId}/`,
      poData
    );
    return response.data;
  } catch (error) {
    throw formatError(error);
  }
};

export const receivePurchaseOrderItems = async (
  poId: number,
  itemsReceived: { id: number; received_quantity: number }[]
): Promise<PurchaseOrder> => {
  try {
    // Envia apenas os IDs dos itens do PO e a quantidade recebida
    const response = await api.post<PurchaseOrder>(
      `${BASE_URL_POS}/${poId}/receive_items/`,
      { items: itemsReceived }
    );
    return response.data;
  } catch (error) {
    throw formatError(error);
  }
};

export const deletePurchaseOrder = async (poId: number): Promise<void> => {
  try {
    await api.delete(`${BASE_URL_POS}/${poId}/`);
  } catch (error) {
    throw formatError(error);
  }
};
