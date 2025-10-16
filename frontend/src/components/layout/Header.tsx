import { Button } from '../common';
import LanguageSelector from '../common/LanguageSelector';

interface HeaderProps {
  onAddProduct?: () => void;
}

const Header = ({ onAddProduct }: HeaderProps) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">L</span>
            </div>
            <span className="text-xl font-semibold text-gray-800">logoipsum</span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <a href="/dashboard" className="text-purple-600 font-medium hover:text-purple-700">
              Dashboard
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900">
              Orders
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900">
              Promotion
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900">
              Inbox
            </a>
          </nav>

          {/* Right side actions */}
          <div className="flex items-center gap-4">
            <Button
              variant="primary"
              onClick={onAddProduct}
              className="bg-purple-600 hover:bg-purple-700"
            >
              Add New Product
            </Button>

            {/* Notification Bell */}
            <button className="relative p-2 text-gray-600 hover:text-gray-900">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>

            <LanguageSelector />

            {/* User Avatar */}
            <div className="w-10 h-10 bg-gray-300 rounded-full overflow-hidden">
              <img
                src="https://api.dicebear.com/7.x/avataaars/svg?seed=user"
                alt="User avatar"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;