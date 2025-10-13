import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';

const NavBar = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();

  const handleLogout = async () => {
    try {
      await authService.logout();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo e título */}
          <div className="flex items-center space-x-4">
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
                {user?.first_name || user?.username || 'User'}
              </span>
              <span className="text-xs text-gray-500">{user?.email}</span>
            </div>

            {/* Avatar */}
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-500 rounded-full text-white font-semibold text-sm shadow-md">
              {(user?.first_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}
            </div>

            {/* Botões */}
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-xl transition-all duration-300 shadow-md hover:shadow-lg transform hover:scale-105"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="font-medium">Logout</span>
            </button>
            <button
              onClick={() => navigate('/checkout')}
              className="ml-2 hidden md:inline-flex items-center space-x-2 px-4 py-2 border border-orange-500 text-orange-600 rounded-xl hover:bg-orange-50"
            >
              <span>Checkout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
