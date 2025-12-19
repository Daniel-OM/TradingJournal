import axios from 'axios';
import type { PerformanceStats, SymbolPerformance } from '../types/api';

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

export const performanceService = {
  // Get overall performance stats
  getStats: async (filters?: {
    date_from?: string;
    date_to?: string;
  }) => {
    const response = await axiosInstance.get<PerformanceStats>(
      '/performance/stats',
      { params: filters }
    );
    return response.data;
  },

  // Get performance by symbol
  getBySymbol: async (filters?: {
    date_from?: string;
    date_to?: string;
  }) => {
    const response = await axiosInstance.get<SymbolPerformance[]>(
      '/performance/symbols',
      { params: filters }
    );
    return response.data;
  },

  // Get monthly performance
  getMonthly: async () => {
    const response = await axiosInstance.get('/performance/monthly');
    return response.data;
  },

  // Get daily performance
  getDaily: async () => {
    const response = await axiosInstance.get('/performance/daily');
    return response.data;
  },
};
