// Novo arquivo: frontend/src/pages/PurchaseOrderPage.tsx

import React, { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
// CORREÇÃO 1: Removendo useNavigate não utilizado.
import {
  getPurchaseOrders,
  getSuppliers,
  createPurchaseOrder,
  receivePurchaseOrderItems,
  // getPurchaseOrder, // Removido por não ser usado
  // updatePurchaseOrder // Removido por não ser usado
} from "../services/purchaseOrderService";
import { getProducts } from "../services/productService"; // CORREÇÃO 2: Importação direta
import { useStore } from "../hooks/useStore"; // CORREÇÃO 3: Importação direta
import {
  PurchaseOrder,
  Supplier,
  PurchaseOrderItem,
  PurchaseOrderCreatePayload,
} from "../types/purchaseOrder";
// CORREÇÃO 4: Ajuste na importação de tipos
import { Product, ProductVariant } from "../types/product";
import { Button, Card, Input } from "../components/common";
import ApiErrorAlert from "../components/common/ApiErrorAlert"; // CORREÇÃO 5: Importação direta
import { Loader2 } from "lucide-react"; // CORREÇÃO 6: Importação de lucide-react
import useAuth from "../hooks/useAuth"; // CORREÇÃO 7: Importação de useAuth (presume-se export default)

const PO_STATUS_MAP: { [key in PurchaseOrder["status"]]: string } = {
  DRAFT: "Rascunho",
  PENDING: "Pendente",
  ORDERED: "Pedido",
  RECEIVED_PARTIAL: "Recebido Parcial",
  RECEIVED_FULL: "Recebido Total",
  CANCELLED: "Cancelado",
};

// Componente de Modal/Formulário de Criação de PO (Simplificado)
type NewPOModalProps = {
  storeId: number;
  suppliers: Supplier[];
  variants: ProductVariant[];
  onClose: () => void;
  onSuccess: () => void;
};

const NewPOModal: React.FC<NewPOModalProps> = ({
  storeId,
  suppliers,
  variants,
  onClose,
  onSuccess,
}) => {
  const { t } = useTranslation();
  const [supplier, setSupplier] = useState<number | "">("");
  const [expectedDeliveryDate, setExpectedDeliveryDate] = useState("");
  const [items, setItems] = useState<
    Omit<
      PurchaseOrderItem,
      | "id"
      | "purchase_order"
      | "variant_name"
      | "product_name"
      | "sku"
      | "total_cost"
    >[]
  >([{ variant: 0, ordered_quantity: 1, received_quantity: 0, unit_cost: 0 }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddItem = () => {
    setItems([
      ...items,
      { variant: 0, ordered_quantity: 1, received_quantity: 0, unit_cost: 0 },
    ]);
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const newItems = items.map((item, i) => {
      if (i === index) {
        return { ...item, [field]: value };
      }
      return item;
    });
    setItems(newItems);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (
      !supplier ||
      items.some((item) => !item.variant || item.ordered_quantity <= 0)
    ) {
      setError(t("Selecione um fornecedor e adicione itens válidos."));
      return;
    }

    setLoading(true);
    setError(null);

    // CORREÇÃO 8: A propriedade 'store' deve ser passada diretamente no payload
    const payload = {
      store: storeId, // Adicionando o storeId aqui
      supplier: Number(supplier),
      status: "ORDERED", // Cria como ORDENADO
      expected_delivery_date: expectedDeliveryDate || null,
      notes: "",
      po_items: items.map((item) => ({
        ...item,
        variant: Number(item.variant),
        unit_cost: Number(item.unit_cost),
      })),
    } as PurchaseOrderCreatePayload & { store: number }; // Adicionando tipagem temporária para 'store'

    try {
      await createPurchaseOrder(payload as any);
      onSuccess();
      onClose();
    } catch (err) {
      setError(
        t("Falha ao criar o Pedido de Compra: ") + (err as Error).message
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="bg-white w-full max-w-4xl p-6 overflow-y-auto max-h-[90vh]">
        <h2 className="text-xl font-bold mb-4">{t("Novo Pedido de Compra")}</h2>

        {error && <ApiErrorAlert error={error} />}

        <form onSubmit={handleSubmit}>
          {/* Seleção de Fornecedor */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              {t("Fornecedor")}
            </label>
            <select
              value={supplier}
              onChange={(e) => setSupplier(Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
              required
            >
              <option value="">{t("Selecione um fornecedor")}</option>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Data de Entrega Prevista */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              {t("Data de Entrega Prevista")}
            </label>
            <Input
              type="date"
              value={expectedDeliveryDate}
              onChange={(e) => setExpectedDeliveryDate(e.target.value)}
            />
          </div>

          {/* Itens do Pedido */}
          <h3 className="text-lg font-semibold my-4">{t("Itens do Pedido")}</h3>
          <div className="space-y-4">
            {items.map((item, index) => (
              <div
                key={index}
                className="flex flex-col sm:flex-row gap-4 border p-4 rounded-lg bg-gray-50"
              >
                {/* Variante do Produto */}
                <div className="flex-1">
                  <label className="block text-xs font-medium text-gray-600">
                    {t("Variante do Produto")}
                  </label>
                  <select
                    value={item.variant}
                    onChange={(e) =>
                      handleItemChange(index, "variant", Number(e.target.value))
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm text-sm p-2"
                    required
                  >
                    <option value={0}>{t("Selecione a variante")}</option>
                    {variants.map((v) => (
                      <option key={v.id} value={v.id}>
                        {/* CORREÇÃO 9: Acessa o nome do produto no objeto Product dentro da variante */}
                        {(v.product as unknown as Product).name} ({v.sku}) -{" "}
                        {v.color || ""} {v.size || ""}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Quantidade Pedida */}
                <div className="w-full sm:w-1/4">
                  <label className="block text-xs font-medium text-gray-600">
                    {t("Qtd Pedida")}
                  </label>
                  <Input
                    type="number"
                    value={item.ordered_quantity}
                    onChange={(e) =>
                      handleItemChange(
                        index,
                        "ordered_quantity",
                        Number(e.target.value)
                      )
                    }
                    min="1"
                    required
                  />
                </div>

                {/* Custo Unitário */}
                <div className="w-full sm:w-1/4">
                  <label className="block text-xs font-medium text-gray-600">
                    {t("Custo Unitário")}
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    value={item.unit_cost}
                    onChange={(e) =>
                      handleItemChange(
                        index,
                        "unit_cost",
                        Number(e.target.value)
                      )
                    }
                    min="0"
                    required
                  />
                </div>

                {/* Botão de Remover */}
                <div className="flex items-end pt-2 sm:pt-0">
                  <Button
                    type="button"
                    variant="danger"
                    onClick={() => handleRemoveItem(index)}
                    className="h-10 w-10 p-0"
                  >
                    &times;
                  </Button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex justify-between">
            <Button type="button" variant="secondary" onClick={handleAddItem}>
              {t("Adicionar Item")}
            </Button>
            <div className="flex gap-2">
              <Button type="button" variant="secondary" onClick={onClose}>
                {t("Cancelar")}
              </Button>
              <Button type="submit" disabled={loading || items.length === 0}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {t("Criar PO")}
              </Button>
            </div>
          </div>
        </form>
      </Card>
    </div>
  );
};

// Componente principal da Página de Pedidos de Compra
const PurchaseOrderPage: React.FC = () => {
  const { t } = useTranslation();
  const { store } = useStore();
  const { user } = useAuth();
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  // const [products, setProducts] = useState<Product[]>([]); // Removido por não ser usado diretamente
  const [variants, setVariants] = useState<ProductVariant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [expandedPO, setExpandedPO] = useState<number | null>(null);

  const storeId = store?.id;

  const fetchPOs = useCallback(async () => {
    if (!storeId) return;
    setLoading(true);
    setError(null);
    try {
      const pos = await getPurchaseOrders(storeId);
      setPurchaseOrders(pos);
    } catch (err) {
      setError(
        t("Erro ao carregar Pedidos de Compra: ") + (err as Error).message
      );
    } finally {
      setLoading(false);
    }
  }, [storeId, t]);

  const fetchDependencies = useCallback(async () => {
    if (!storeId) return;
    try {
      const [suppliersData, productsData] = await Promise.all([
        getSuppliers(storeId),
        getProducts(storeId),
      ]);

      setSuppliers(suppliersData);
      // setProducts(productsData); // Não é necessário manter no state

      // Extrair todas as variantes em um array único e garantir a tipagem correta
      const allVariants = productsData.flatMap(
        (
          p: Product // CORREÇÃO 10: Tipagem explícita para 'p'
        ) =>
          p.variants.map(
            (v: ProductVariant) => ({ ...v, product: p } as ProductVariant)
          ) // CORREÇÃO 11: Tipagem explícita para 'v' e correta associação
      );
      setVariants(allVariants);
    } catch (err) {
      setError(
        t("Erro ao carregar dependências (Fornecedores/Produtos): ") +
          (err as Error).message
      );
    }
  }, [storeId, t]);

  useEffect(() => {
    if (storeId) {
      fetchPOs();
      fetchDependencies();
    }
  }, [storeId, fetchPOs, fetchDependencies]);

  // CORREÇÃO 12: Removida a função handleReceiveItems não utilizada.
  // A função é implementada e utilizada no componente ReceiveItemForm.

  const handleToggleExpand = (poId: number) => {
    setExpandedPO(expandedPO === poId ? null : poId);
  };

  if (!user) {
    return (
      <Card className="text-center p-8">
        {t("Você precisa estar logado para acessar esta página.")}
      </Card>
    );
  }

  if (loading && purchaseOrders.length === 0) {
    return (
      <div className="flex justify-center items-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
        {t("Pedidos de Compra (PO)")}
      </h1>

      {error && <ApiErrorAlert error={error} />}

      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-700">
          {t("Gerenciamento de Entrada de Estoque")}
        </h2>
        <Button
          onClick={() => setIsModalOpen(true)}
          disabled={!storeId || suppliers.length === 0 || variants.length === 0}
        >
          {t("Criar Novo PO")}
        </Button>
      </div>

      {isModalOpen && storeId && (
        <NewPOModal
          storeId={storeId}
          suppliers={suppliers}
          variants={variants}
          onClose={() => setIsModalOpen(false)}
          onSuccess={fetchPOs}
        />
      )}

      {purchaseOrders.length === 0 && !loading && (
        <Card className="text-center p-8 text-gray-600">
          <p>{t("Nenhum Pedido de Compra encontrado.")}</p>
          <p>
            {t("Crie um novo PO para dar entrada em estoque de fornecedores.")}
          </p>
        </Card>
      )}

      <div className="space-y-4">
        {purchaseOrders.map((po) => (
          <Card
            key={po.id}
            className="p-4 bg-white shadow-lg border border-gray-100"
          >
            <div
              className="flex flex-col sm:flex-row justify-between items-start sm:items-center cursor-pointer"
              onClick={() => handleToggleExpand(po.id)}
            >
              <div className="flex flex-col">
                <span className="text-sm font-medium text-indigo-600">
                  PO #{po.id}
                </span>
                <span className="text-lg font-semibold">
                  {t("Fornecedor")}: {po.supplier_name}
                </span>
              </div>
              <div className="flex items-center gap-4 mt-2 sm:mt-0">
                <span
                  className={`px-3 py-1 text-sm font-semibold rounded-full ${
                    po.status === "RECEIVED_FULL"
                      ? "bg-green-100 text-green-800"
                      : po.status === "RECEIVED_PARTIAL"
                      ? "bg-yellow-100 text-yellow-800"
                      : po.status === "ORDERED"
                      ? "bg-blue-100 text-blue-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {PO_STATUS_MAP[po.status] || po.status}
                </span>
                <span className="text-gray-500 font-medium">
                  {t("Custo Total")}: {po.total_cost.toFixed(2)}{" "}
                  {store?.currency}
                </span>
                <span className="text-gray-400">
                  {expandedPO === po.id ? "▲" : "▼"}
                </span>
              </div>
            </div>

            {expandedPO === po.id && (
              <div className="mt-4 border-t pt-4">
                <p className="text-sm text-gray-500 mb-4">
                  {t("Data do Pedido")}:{" "}
                  {new Date(po.order_date).toLocaleDateString()}
                </p>

                <h4 className="font-bold mb-2">{t("Itens do Pedido")}</h4>
                <div className="space-y-3">
                  {po.po_items.map((item) => {
                    const received = item.received_quantity;
                    const ordered = item.ordered_quantity;
                    const pending = ordered - received;
                    const isComplete = pending === 0;

                    return (
                      <div
                        key={item.id}
                        className="border-l-4 border-indigo-500 pl-3 py-2 bg-white flex flex-wrap justify-between items-center text-sm"
                      >
                        <div>
                          <p className="font-semibold">
                            {item.variant_name || item.product_name}
                          </p>
                          <p className="text-xs text-gray-500">
                            SKU: {item.sku}
                          </p>
                        </div>
                        <div className="flex items-center gap-4 text-gray-700">
                          <span>
                            {t("Qtd Pedida")}: {ordered}
                          </span>
                          <span>
                            {t("Qtd Recebida")}: {received}
                          </span>
                          <span
                            className={`${
                              isComplete ? "text-green-600" : "text-red-600"
                            }`}
                          >
                            {t("Pendente")}: {pending}
                          </span>
                          <span>
                            {t("Custo Unitário")}: {item.unit_cost.toFixed(2)}
                          </span>
                        </div>

                        {/* Formulário de Recebimento */}
                        {pending > 0 && po.status !== "CANCELLED" && (
                          <ReceiveItemForm
                            poId={po.id}
                            item={item}
                            maxReceive={pending}
                            onReceive={fetchPOs} // Passa fetchPOs como callback de sucesso
                            onError={setError}
                          />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
};

// Componente para formulário de recebimento
type ReceiveItemFormProps = {
  poId: number;
  item: PurchaseOrderItem;
  maxReceive: number;
  onReceive: () => void;
  onError: (error: string | null) => void;
};

const ReceiveItemForm: React.FC<ReceiveItemFormProps> = ({
  poId,
  item,
  maxReceive,
  onReceive,
  onError,
}) => {
  const { t } = useTranslation();
  const [quantity, setQuantity] = useState(maxReceive);
  const [receiving, setReceiving] = useState(false);

  const handleReceiveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (quantity <= 0 || quantity > maxReceive) {
      onError(t("Quantidade de recebimento inválida."));
      return;
    }

    setReceiving(true);
    onError(null);
    try {
      await receivePurchaseOrderItems(poId, [
        { id: item.id, received_quantity: quantity },
      ]);
      onReceive();
    } catch (err) {
      onError(t("Erro ao registrar recebimento: ") + (err as Error).message);
    } finally {
      setReceiving(false);
    }
  };

  return (
    <form
      onSubmit={handleReceiveSubmit}
      className="flex items-center gap-2 mt-2 w-full sm:w-auto"
    >
      <Input
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(Number(e.target.value))}
        min="1"
        max={maxReceive}
        className="w-24 text-sm"
        required
      />
      <Button
        type="submit"
        size="sm"
        disabled={receiving || quantity <= 0 || quantity > maxReceive}
      >
        {receiving && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
        {t("Receber")}
      </Button>
    </form>
  );
};

export default PurchaseOrderPage;
