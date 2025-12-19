import { create } from 'zustand';
import type { Strategy, StrategyCreate } from '../types/api';
import { strategyService } from '../services/strategyService';

interface StrategyStore {
  strategies: Strategy[];
  currentStrategy: Strategy | null;
  loading: boolean;
  error: string | null;

  fetchStrategies: () => Promise<void>;
  fetchStrategy: (id: string) => Promise<void>;
  createStrategy: (data: StrategyCreate) => Promise<Strategy>;
  updateStrategy: (id: string, data: Partial<StrategyCreate>) => Promise<Strategy>;
  deleteStrategy: (id: string) => Promise<void>;
  setCurrentStrategy: (strategy: Strategy | null) => void;
  clearError: () => void;
}

export const useStrategyStore = create<StrategyStore>((set) => ({
  strategies: [],
  currentStrategy: null,
  loading: false,
  error: null,

  fetchStrategies: async () => {
    set({ loading: true, error: null });
    try {
      const strategies = await strategyService.getAll();
      set({ strategies });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching strategies' });
    } finally {
      set({ loading: false });
    }
  },

  fetchStrategy: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const strategy = await strategyService.getById(id);
      set({ currentStrategy: strategy });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching strategy' });
    } finally {
      set({ loading: false });
    }
  },

  createStrategy: async (data: StrategyCreate) => {
    set({ loading: true, error: null });
    try {
      const newStrategy = await strategyService.create(data);
      set((state) => ({
        strategies: [...state.strategies, newStrategy],
      }));
      return newStrategy;
    } catch (error: any) {
      set({ error: error.message || 'Error creating strategy' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  updateStrategy: async (id: string, data: Partial<StrategyCreate>) => {
    set({ loading: true, error: null });
    try {
      const updated = await strategyService.update(id, data);
      set((state) => ({
        strategies: state.strategies.map((s) => (s.id === id ? updated : s)),
        currentStrategy: state.currentStrategy?.id === id ? updated : state.currentStrategy,
      }));
      return updated;
    } catch (error: any) {
      set({ error: error.message || 'Error updating strategy' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  deleteStrategy: async (id: string) => {
    set({ loading: true, error: null });
    try {
      await strategyService.delete(id);
      set((state) => ({
        strategies: state.strategies.filter((s) => s.id !== id),
        currentStrategy: state.currentStrategy?.id === id ? null : state.currentStrategy,
      }));
    } catch (error: any) {
      set({ error: error.message || 'Error deleting strategy' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  setCurrentStrategy: (strategy: Strategy | null) => {
    set({ currentStrategy: strategy });
  },

  clearError: () => {
    set({ error: null });
  },
}));
