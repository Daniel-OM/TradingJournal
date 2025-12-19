import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-card-bg border-b border-white/10 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 hover:opacity-80 transition">
            <i className="fas fa-chart-line text-2xl text-primary"></i>
            <span className="text-xl font-bold text-white hidden sm:inline">Trading Journal</span>
          </Link>

          {/* Desktop Menu */}
          {isAuthenticated && (
            <div className="hidden md:flex space-x-1">
              <NavLink to="/">Home</NavLink>
              <NavLink to="/watchlists">Watchlist</NavLink>
              <NavLink to="/trades">Journal</NavLink>
              <NavLink to="/performance">Performance</NavLink>
              <NavLink to="/improvements">Improvements</NavLink>
              <NavLink to="/strategies">Strategies</NavLink>
              <NavLink to="/screeners">Screeners</NavLink>
              <NavLink to="/assets">Assets</NavLink>
              <NavLink to="/settings">Settings</NavLink>
            </div>
          )}

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user && (
              <span className="hidden md:block text-sm text-text-muted">
                {user.username}
              </span>
            )}

            {/* Mobile Toggle */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden text-2xl text-text-muted hover:text-white transition"
            >
              <i className={`fas fa-${isOpen ? 'xmark' : 'bars'}`}></i>
            </button>

            {/* Auth Buttons */}
            {!isAuthenticated ? (
              <div className="hidden md:flex space-x-2">
                <Link
                  to="/login"
                  className="btn-pill bg-primary text-white text-sm"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="btn-pill bg-secondary text-white text-sm"
                >
                  Register
                </Link>
              </div>
            ) : (
              <button
                onClick={handleLogout}
                className="btn-pill bg-danger text-white text-sm hidden md:block"
              >
                Logout
              </button>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && isAuthenticated && (
          <div className="md:hidden pb-4 space-y-2">
            <MobileNavLink to="/" onClick={() => setIsOpen(false)}>
              Home
            </MobileNavLink>
            <MobileNavLink to="/watchlists" onClick={() => setIsOpen(false)}>
              Watchlist
            </MobileNavLink>
            <MobileNavLink to="/trades" onClick={() => setIsOpen(false)}>
              Journal
            </MobileNavLink>
            <MobileNavLink to="/performance" onClick={() => setIsOpen(false)}>
              Performance
            </MobileNavLink>
            <MobileNavLink to="/improvements" onClick={() => setIsOpen(false)}>
              Improvements
            </MobileNavLink>
            <MobileNavLink to="/strategies" onClick={() => setIsOpen(false)}>
              Strategies
            </MobileNavLink>
            <MobileNavLink to="/screeners" onClick={() => setIsOpen(false)}>
              Screeners
            </MobileNavLink>
            <MobileNavLink to="/assets" onClick={() => setIsOpen(false)}>
              Assets
            </MobileNavLink>
            <MobileNavLink to="/settings" onClick={() => setIsOpen(false)}>
              Settings
            </MobileNavLink>
            <button
              onClick={() => {
                handleLogout();
                setIsOpen(false);
              }}
              className="btn-pill bg-danger text-white w-full text-sm mt-2"
            >
              Logout
            </button>
          </div>
        )}

        {/* Mobile Auth Buttons */}
        {!isAuthenticated && isOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link
              to="/login"
              className="btn-pill bg-primary text-white w-full block text-center text-sm"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="btn-pill bg-secondary text-white w-full block text-center text-sm"
            >
              Register
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

interface NavLinkProps {
  to: string;
  children: React.ReactNode;
}

const NavLink: React.FC<NavLinkProps> = ({ to, children }) => (
  <Link
    to={to}
    className="text-text-secondary hover:text-primary transition px-3 py-2 rounded-lg hover:bg-white/5"
  >
    {children}
  </Link>
);

interface MobileNavLinkProps {
  to: string;
  children: React.ReactNode;
  onClick: () => void;
}

const MobileNavLink: React.FC<MobileNavLinkProps> = ({ to, children, onClick }) => (
  <Link
    to={to}
    onClick={onClick}
    className="block text-text-secondary hover:text-primary transition px-3 py-2 rounded-lg hover:bg-white/5"
  >
    {children}
  </Link>
);
