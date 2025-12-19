export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Trade {
  id: number;
  user_id: number;
  symbol: string;
  company_name?: string;
  entry_date: string;
  entry_time?: string;
  entry_price: number;
  exit_date?: string;
  exit_time?: string;
  exit_price?: number;
  quantity: number;
  exit_quantity?: number;
  trade_type: 'LONG' | 'SHORT';
  balance?: number;
  commission: number;
  profit_loss?: number;
  description?: string;
  why_profitable?: string;
  influencing_factors?: string;
  hashtags?: string;
  stop_loss?: number;
  take_profit?: number;
  strategy_id?: number;
  created_at: string;
  updated_at: string;
  strategy?: Strategy;
  transactions?: Transaction[];
  media?: Media[];
}

export interface Strategy {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  conditions?: StrategyCondition[];
}

export interface StrategyCondition {
  id: number;
  strategy_id: number;
  name: string;
  description?: string;
  score: number;
  created_at: string;
  updated_at: string;
}

export interface Watchlist {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  entries?: WatchlistEntry[];
}

export interface WatchlistEntry {
  id: number;
  watchlist_id: number;
  symbol: string;
  date: string;
  date_exit?: string;
  entry_price: number;
  exit_price?: number;
  reason?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: number;
  trade_id: number;
  date: string;
  time?: string;
  price: number;
  quantity: number;
  type: 'BUY' | 'SELL';
  commission: number;
  ecn_fee: number;
  locates: number;
  created_at: string;
}

export interface Media {
  id: number;
  trade_id: number;
  url: string;
  type?: string;
  created_at: string;
}

export interface Error {
  id: number;
  user_id: number;
  description: string;
  category?: string;
  severity?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PerformanceStats {
  total_pnl: number;
  winning_trades: number;
  losing_trades: number;
  scratch_trades: number;
  win_rate: number;
  loss_rate: number;
  winning_pnl: number;
  losing_pnl: number;
  avg_trade_pnl: number;
  avg_pnl_per_share: number;
  median_trade_pnl: number;
  avg_win: number;
  avg_loss: number;
  largest_gain: number;
  largest_loss: number;
  risk_reward: number;
  total_wins: number;
  total_losses: number;
  profit_factor: number;
  trade_pnl_std: number;
  sharpe_ratio: number;
  max_drawdown: number;
  sqn: number;
  k_ratio: number;
  kelly_percent: number;
  p_value: number;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
  avg_daily_pnl: number;
  avg_daily_volume: number;
  avg_win_per_day: number;
  avg_loss_per_day: number;
  daily_winrate: number;
  avg_trades_per_day: number;
}

export interface SymbolPerformance {
  symbol: string;
  total_pnl: number;
  avg_pnl: number;
  win_rate: number;
  trade_count: number;
  avg_win: number;
  avg_loss: number;
}

export interface BestWorstSymbols {
  best: SymbolPerformance[];
  worst: SymbolPerformance[];
}

export interface PerformanceData {
  stats: PerformanceStats;
  best_worst_symbols: BestWorstSymbols;
}
