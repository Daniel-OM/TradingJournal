import axios from 'axios';
import type { Asset } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const assetService = {
  // Get screener data
  getScreener: async (filters?: {
    search?: string;
    min_price?: number;
    max_price?: number;
    min_volume?: number;
    skip?: number;
    limit?: number;
  }) => {
    const response = await axiosInstance.get<Asset[]>('/assets/screener', {
      params: filters,
    });
    return response.data;
  },

  // Get asset details
  getDetails: async (symbol: string) => {
    const response = await axiosInstance.get(`/assets/${symbol}`);
    return response.data;
  },

  // Get asset candles (OHLCV)
  getCandles: async (
    symbol: string,
    timeframe: '1m' | '5m' | '15m' | '1h' | '1d' = '1d'
  ) => {
    const response = await axiosInstance.get(
      `/assets/${symbol}/candles`,
      { params: { timeframe } }
    );
    return response.data;
  },
};
