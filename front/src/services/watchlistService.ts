import axios from 'axios';
import type {
  Watchlist,
  WatchlistCreate,
  WatchlistEntry,
  WatchlistEntryCreate,
} from '../types/api';

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

export const watchlistService = {
  // Get all watchlists
  getAll: async () => {
    const response = await axiosInstance.get<Watchlist[]>('/watchlists');
    return response.data;
  },

  // Get single watchlist
  getById: async (id: string) => {
    const response = await axiosInstance.get<Watchlist>(`/watchlists/${id}`);
    return response.data;
  },

  // Create watchlist
  create: async (data: WatchlistCreate) => {
    const response = await axiosInstance.post<Watchlist>('/watchlists', data);
    return response.data;
  },

  // Update watchlist
  update: async (id: string, data: Partial<WatchlistCreate>) => {
    const response = await axiosInstance.put<Watchlist>(`/watchlists/${id}`, data);
    return response.data;
  },

  // Delete watchlist
  delete: async (id: string) => {
    await axiosInstance.delete(`/watchlists/${id}`);
  },

  // Get watchlist entries
  getEntries: async (watchlistId: string) => {
    const response = await axiosInstance.get<WatchlistEntry[]>(
      `/watchlists/${watchlistId}/entries`
    );
    return response.data;
  },

  // Add entry to watchlist
  addEntry: async (watchlistId: string, data: WatchlistEntryCreate) => {
    const response = await axiosInstance.post<WatchlistEntry>(
      `/watchlists/${watchlistId}/entries`,
      data
    );
    return response.data;
  },

  // Update watchlist entry
  updateEntry: async (watchlistId: string, entryId: string, data: Partial<WatchlistEntryCreate>) => {
    const response = await axiosInstance.put<WatchlistEntry>(
      `/watchlists/${watchlistId}/entries/${entryId}`,
      data
    );
    return response.data;
  },

  // Delete watchlist entry
  deleteEntry: async (watchlistId: string, entryId: string) => {
    await axiosInstance.delete(`/watchlists/${watchlistId}/entries/${entryId}`);
  },
};
