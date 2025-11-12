import { useNavigate } from "react-router-dom";
import { Badge, Dropdown } from "antd";
import { ShoppingCartOutlined, ShoppingOutlined } from "@ant-design/icons";
import type { MenuProps } from "antd";
import authService from "../../services/authService";
import { useCart } from "../../context/CartContext";

const NavBar = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();
  const { state } = useCart();
  const isAdmin = user?.is_staff || user?.is_superuser;

  // Calcula total de itens no carrinho
  const totalItems = state.items.reduce((sum, item) => sum + item.quantity, 0);

  // Menu dropdown do usuário
  const userMenuItems: MenuProps["items"] = [
    {
      key: "orders",
      label: "Meus Pedidos",
      icon: <ShoppingOutlined />,
      onClick: () => navigate("/orders"),
    },
    {
      type: "divider",
    },
    {
      key: "logout",
      label: "Sair",
      danger: true,
      onClick: handleLogout,
    },
  ];

  async function handleLogout() {
    try {
      await authService.logout();
      navigate("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  }

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo e título */}
          <div
            className="flex items-center space-x-4 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => navigate("/home")}
          >
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-md">
              <span className="text-2xl">⚡</span>
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
              ThunderShoes
            </h1>
          </div>

          {/* Informações do usuário e logout */}
          <div className="flex items-center space-x-4">
            {/* Info do usuário */}
            <div className="hidden md:flex flex-col items-end">
              <span className="text-sm font-medium text-gray-900">
                {user?.first_name || user?.username || "User"}
              </span>
              <span className="text-xs text-gray-500">{user?.email}</span>
            </div>

            {/* Botão Meus Pedidos (apenas para não-admin) */}
            {!isAdmin && (
              <button
                onClick={() => navigate("/orders")}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white rounded-xl transition-all duration-300 shadow-md hover:shadow-lg transform hover:scale-105"
              >
                <ShoppingOutlined style={{ fontSize: "20px" }} />
                <span className="font-medium hidden md:inline">Pedidos</span>
              </button>
            )}

            {/* Botão do Carrinho com Badge */}
            <Badge count={totalItems} offset={[-5, 5]} showZero={false}>
              <button
                onClick={() => navigate("/cart")}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-xl transition-all duration-300 shadow-md hover:shadow-lg transform hover:scale-105"
              >
                <ShoppingCartOutlined style={{ fontSize: "20px" }} />
                <span className="font-medium hidden md:inline">Carrinho</span>
              </button>
            </Badge>

            {/* Avatar com Dropdown */}
            <Dropdown
              menu={{ items: userMenuItems }}
              trigger={["click"]}
              placement="bottomRight"
            >
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-500 rounded-full text-white font-semibold text-sm shadow-md cursor-pointer hover:shadow-lg transition-shadow">
                {(
                  user?.first_name?.[0] ||
                  user?.username?.[0] ||
                  "U"
                ).toUpperCase()}
              </div>
            </Dropdown>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
