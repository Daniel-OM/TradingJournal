import axios from 'axios';
import type { Strategy, StrategyCreate } from '../types/api';

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

export const strategyService = {
  // Get all strategies
  getAll: async () => {
    const response = await axiosInstance.get<Strategy[]>('/strategies');
    return response.data;
  },

  // Get single strategy
  getById: async (id: string) => {
    const response = await axiosInstance.get<Strategy>(`/strategies/${id}`);
    return response.data;
  },

  // Create strategy
  create: async (data: StrategyCreate) => {
    const response = await axiosInstance.post<Strategy>('/strategies', data);
    return response.data;
  },

  // Update strategy
  update: async (id: string, data: Partial<StrategyCreate>) => {
    const response = await axiosInstance.put<Strategy>(`/strategies/${id}`, data);
    return response.data;
  },

  // Delete strategy
  delete: async (id: string) => {
    await axiosInstance.delete(`/strategies/${id}`);
  },
};
