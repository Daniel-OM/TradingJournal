import { create } from 'zustand';
import type { PerformanceStats, SymbolPerformance } from '../types/api';
import { performanceService } from '../services/performanceService';

interface PerformanceStore {
  stats: PerformanceStats | null;
  symbolPerformance: SymbolPerformance[];
  monthlyData: any[];
  dailyData: any[];
  loading: boolean;
  error: string | null;

  fetchStats: (filters?: any) => Promise<void>;
  fetchSymbolPerformance: (filters?: any) => Promise<void>;
  fetchMonthlyData: () => Promise<void>;
  fetchDailyData: () => Promise<void>;
  clearError: () => void;
}

export const usePerformanceStore = create<PerformanceStore>((set) => ({
  stats: null,
  symbolPerformance: [],
  monthlyData: [],
  dailyData: [],
  loading: false,
  error: null,

  fetchStats: async (filters) => {
    set({ loading: true, error: null });
    try {
      const stats = await performanceService.getStats(filters);
      set({ stats });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching performance stats' });
    } finally {
      set({ loading: false });
    }
  },

  fetchSymbolPerformance: async (filters) => {
    set({ loading: true, error: null });
    try {
      const symbolPerformance = await performanceService.getBySymbol(filters);
      set({ symbolPerformance });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching symbol performance' });
    } finally {
      set({ loading: false });
    }
  },

  fetchMonthlyData: async () => {
    set({ loading: true, error: null });
    try {
      const monthlyData = await performanceService.getMonthly();
      set({ monthlyData });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching monthly data' });
    } finally {
      set({ loading: false });
    }
  },

  fetchDailyData: async () => {
    set({ loading: true, error: null });
    try {
      const dailyData = await performanceService.getDaily();
      set({ dailyData });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching daily data' });
    } finally {
      set({ loading: false });
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
