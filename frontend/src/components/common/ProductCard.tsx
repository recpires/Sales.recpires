import React, { FC } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
// 1. IMPORTAR A INTERFACE PRODUCT
import { Product } from "../../types/product";

interface ProductCardProps {
  // 2. USAR A INTERFACE IMPORTADA
  product: Product;
  // 3. TIPAR O PARÂMETRO DA FUNÇÃO PARA REMOVER O 'any'
  onAddToCart?: (product: Product) => void;
  onDelete?: (productId: number) => void;
  isAdmin?: boolean;
}

const ProductCard: FC<ProductCardProps> = ({
  product,
  onAddToCart,
  onDelete,
  isAdmin,
}) => {
  // ... (o restante do código fica igual)
};

export default ProductCard;
