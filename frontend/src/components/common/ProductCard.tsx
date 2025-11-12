import type { FC } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Product } from "../../types/product";
import { Button } from "./Button"; // Você já tem esse componente na pasta 'common'
import { ShoppingCart, Trash2, Edit } from "lucide-react"; // Ícones modernos

interface ProductCardProps {
  product: Product;
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
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Navega para a página de detalhes (cliente) ou edição (admin)
  const handleCardClick = () => {
    if (isAdmin) {
      navigate(`/admin/product/${product.id}`);
    } else {
      navigate(`/product/${product.id}`);
    }
  };

  // Para o clique no botão "Adicionar"
  const handleAddToCartClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Impede que o clique no botão ative o handleCardClick
    if (onAddToCart) {
      onAddToCart(product);
    }
  };

  // Para o clique no botão "Deletar"
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Impede o clique no card
    if (onDelete) {
      onDelete(product.id);
    }
  };

  // Para o clique no botão "Editar"
  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Impede o clique no card
    navigate(`/admin/product/${product.id}`);
  };

  // Imagem fallback caso o produto não tenha imagem
  const imageUrl =
    product.image || "https://via.placeholder.com/300x300.png?text=Sem+Imagem";

  // Formata o preço para R$ 00,00
  // <--- CORREÇÃO 1: Adicionado `(product.price || 0)` para tratar preço opcional
  const formattedPrice = `R$ ${(product.price || 0)
    .toFixed(2)
    .replace(".", ",")}`;

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col justify-between transition-all duration-300 ease-in-out hover:shadow-2xl group border border-gray-100">
      {/* Secção da Imagem */}
      <div className="relative cursor-pointer" onClick={handleCardClick}>
        <img
          src={imageUrl}
          alt={product.name}
          className="w-full h-56 object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {/* Badge de "Esgotado" */}
        {/* <--- CORREÇÃO 2: Trocado `product.total_stock` por `(product.stock || 0)` */}
        {(product.stock || 0) === 0 && !isAdmin && (
          <span className="absolute top-2 left-2 bg-red-600 text-white text-xs font-bold px-3 py-1 rounded-full uppercase z-10">
            {t("common.outOfStock", "Esgotado")}
          </span>
        )}
        {/* Overlay moderno que aparece no hover */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity duration-300 flex items-center justify-center">
          <span className="text-white text-lg font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            {isAdmin
              ? t("common.edit", "Editar")
              : t("common.viewDetails", "Ver Detalhes")}
          </span>
        </div>
      </div>

      {/* Secção de Conteúdo (Nome, Descrição, Preço) */}
      <div className="p-4 flex flex-col flex-grow">
        <h3
          className="text-lg font-semibold text-gray-800 truncate cursor-pointer hover:text-blue-700"
          onClick={handleCardClick}
          title={product.name}
        >
          {product.name}
        </h3>

        {/* Mostra uma descrição curta */}
        <p className="text-sm text-gray-600 mt-1 flex-grow">
          {(product.description?.substring(0, 50) || "Descrição do produto") +
            "..."}
        </p>

        <p className="text-2xl font-bold text-gray-900 mt-2">
          {formattedPrice}
        </p>
      </div>

      {/* Secção de Ações (Botões) */}
      <div className="p-4 border-t border-gray-100 bg-gray-50">
        {isAdmin ? (
          // Botões para o Admin
          <div className="flex space-x-2">
            <Button
              onClick={handleEditClick}
              variant="secondary"
              className="w-full"
            >
              <Edit size={16} className="mr-2" />
              {t("common.edit", "Editar")}
            </Button>
            <Button
              onClick={handleDeleteClick}
              variant="danger"
              className="w-full"
            >
              <Trash2 size={16} className="mr-2" />
              {t("common.delete", "Deletar")}
            </Button>
          </div>
        ) : (
          // Botão para o Cliente
          <Button
            onClick={handleAddToCartClick}
            // <--- CORREÇÃO 3: Trocado `product.total_stock` por `(product.stock || 0)`
            disabled={(product.stock || 0) === 0 || !onAddToCart}
            className="w-full"
          >
            <ShoppingCart size={18} className="mr-2" />
            {(product.stock || 0) > 0 // <--- E AQUI TAMBÉM
              ? t("common.addToCart", "Adicionar")
              : t("common.outOfStock", "Esgotado")}
          </Button>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
