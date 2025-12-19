import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1';

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
  pnl?: number;
  notes?: string;
  description?: string;
  why_profitable?: string;
  influencing_factors?: string;
  hashtags?: string;
  stop_loss?: number;
  take_profit?: number;
  strategy_id?: string;
  created_at: string;
  updated_at: string;
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

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Add token to requests
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const tradeService = {
  // Get all trades with filters
  getAll: async (filters?: {
    symbol?: string;
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }) => {
    const response = await axiosInstance.get<Trade[]>('/trades', { params: filters });
    return response.data;
  },

  // Get trades for a specific month
  getByMonth: async (year: number, month: number) => {
    const response = await axiosInstance.get<Trade[]>(`/trades/month/${year}/${month}`);
    return response.data;
  },

  // Get single trade
  getById: async (id: string) => {
    const response = await axiosInstance.get<Trade>(`/trades/${id}`);
    return response.data;
  },

  // Create trade
  create: async (data: TradeCreate) => {
    const response = await axiosInstance.post<Trade>('/trades', data);
    return response.data;
  },

  // Update trade
  update: async (id: string, data: Partial<TradeCreate>) => {
    const response = await axiosInstance.put<Trade>(`/trades/${id}`, data);
    return response.data;
  },

  // Delete trade
  delete: async (id: string) => {
    await axiosInstance.delete(`/trades/${id}`);
  },

  // Import trades from CSV
  importCSV: async (file: File, timezone: string, dryRun?: boolean) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('timezone', timezone);
    if (dryRun) formData.append('dry_run', 'true');

    const response = await axiosInstance.post('/trades/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
