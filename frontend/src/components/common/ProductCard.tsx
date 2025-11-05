import type { FC } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

interface ProductCardProps {
  product: {
    id: number;
    name?: string;
    description?: string;
    image?: string | null;
  };
  onAddToCart?: (product: any) => void;
  onDelete?: (productId: number) => void;
  isAdmin?: boolean;
}

const ProductCard: FC<ProductCardProps> = ({
  product,
  onAddToCart,
  onDelete,
  isAdmin,
}) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleView = () => navigate(`/products/${product.id}`);
  const handleAdd = () => onAddToCart && onAddToCart(product);
  const handleDelete = () => onDelete && onDelete(product.id);

  return (
    <div className="product-card">
      <img
        src={product.image || "/placeholder.png"}
        alt={product.name || "product"}
      />
      <h3>{product.name}</h3>
      <p>{product.description}</p>
      <div className="product-actions">
        <button onClick={handleView}>{t("View")}</button>
        <button onClick={handleAdd}>{t("Add to cart")}</button>
        {isAdmin && <button onClick={handleDelete}>{t("Delete")}</button>}
      </div>
    </div>
  );
};

export default ProductCard;
