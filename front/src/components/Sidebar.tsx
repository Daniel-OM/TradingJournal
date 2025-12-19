import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

interface NavItem {
  label: string;
  icon: string;
  href: string;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: 'fa-home', href: '/' },
  { label: 'Trades', icon: 'fa-handshake', href: '/trades' },
  { label: 'Strategies', icon: 'fa-chess', href: '/strategies' },
  { label: 'Watchlists', icon: 'fa-list', href: '/watchlists' },
  { label: 'Performance', icon: 'fa-chart-bar', href: '/performance' },
  { label: 'Assets', icon: 'fa-magnifying-glass', href: '/assets' },
  { label: 'Settings', icon: 'fa-gear', href: '/settings' },
];

export function Sidebar() {
  const location = useLocation();
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) return null;

  return (
    <aside className="w-64 bg-slate-800 border-r border-slate-700 overflow-y-auto h-screen">
      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.href}
              to={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
            >
              <i className={`fas ${item.icon} text-lg`}></i>
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
