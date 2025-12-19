// Types para Strategy
export interface Strategy {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  rules?: string;
  created_at: string;
  updated_at: string;
}

export interface StrategyCreate {
  name: string;
  description?: string;
  rules?: string;
}

// Types para Watchlist
export interface Watchlist {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface WatchlistCreate {
  name: string;
  description?: string;
}

export interface WatchlistEntry {
  id: string;
  watchlist_id: string;
  symbol: string;
  alert_price?: number;
  notes?: string;
  created_at: string;
}

export interface WatchlistEntryCreate {
  symbol: string;
  alert_price?: number;
  notes?: string;
}

// Types para Performance
export interface PerformanceStats {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  gross_profit: number;
  gross_loss: number;
  net_profit: number;
  average_win: number;
  average_loss: number;
  profit_factor: number;
  max_drawdown: number;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
}

export interface SymbolPerformance {
  symbol: string;
  trades: number;
  wins: number;
  win_rate: number;
  pnl: number;
  pnl_percent: number;
}

// Types para Asset (Screener)
export interface Asset {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap?: number;
}

// Types para User
export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

// Types para Trade
export interface Trade {
  id: string;
  user_id: string;
  symbol: string;
  company_name?: string;
  trade_type: 'LONG' | 'SHORT';
  entry_date: string;
  entry_time?: string;
  entry_price: number;
  exit_date?: string;
  exit_time?: string;
  exit_price?: number;
  exit_quantity?: number;
  quantity: number;
  balance?: number;
  commission: number;
  profit_loss?: number;
  pnl?: number; // alias for profit_loss
  notes?: string;
  description?: string;
  why_profitable?: string;
  influencing_factors?: string;
  hashtags?: string;
  stop_loss?: number;
  take_profit?: number;
  strategy_id?: string;
  strategy?: Strategy;
  r_multiple?: number;
  created_at: string;
  updated_at: string;
  transactions?: Transaction[];
  ecn_fee?: number; // legacy field
  commission_value?: number; // legacy field
}

export interface TradeCreate {
  symbol: string;
  company_name?: string;
  trade_type: 'LONG' | 'SHORT';
  entry_date: string;
  entry_time?: string;
  entry_price: number;
  exit_date?: string;
  exit_time?: string;
  exit_price?: number;
  exit_quantity?: number;
  quantity: number;
  balance?: number;
  commission?: number;
  profit_loss?: number;
  notes?: string;
  description?: string;
  why_profitable?: string;
  influencing_factors?: string;
  hashtags?: string;
  stop_loss?: number;
  take_profit?: number;
  strategy_id?: string;
}

// Types para Transaction
export interface Transaction {
  id: string;
  trade_id: string;
  transaction_type: 'ENTRY' | 'EXIT' | 'ADJUSTMENT';
  quantity: number;
  price: number;
  commission: number;
  fee?: number;
  date: string;
  timestamp: string;
}
