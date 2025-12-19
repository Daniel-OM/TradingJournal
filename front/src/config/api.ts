// API Constants
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const API_ENDPOINTS = {
  // Auth
  AUTH_REGISTER: '/auth/register',
  AUTH_LOGIN: '/auth/login',
  
  // Users
  USERS_ME: '/users/me',
  
  // Trades
  TRADES: '/trades',
  TRADES_BY_ID: (id: number) => `/trades/${id}`,
  TRADES_STATS: '/performance/stats',
  
  // Strategies
  STRATEGIES: '/strategies',
  STRATEGIES_BY_ID: (id: number) => `/strategies/${id}`,
  
  // Watchlists
  WATCHLISTS: '/watchlists',
  WATCHLISTS_BY_ID: (id: number) => `/watchlists/${id}`,
  
  // Performance
  PERFORMANCE_STATS: '/performance/stats',
  PERFORMANCE_SYMBOLS: '/performance/symbols',
};
