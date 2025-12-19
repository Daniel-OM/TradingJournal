import { create } from 'zustand';
import type { Trade, TradeCreate } from '../services/tradeService';
import { tradeService } from '../services/tradeService';

interface TradeStore {
  trades: Trade[];
  currentTrade: Trade | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchTrades: (filters?: any) => Promise<void>;
  fetchTradesByMonth: (year: number, month: number) => Promise<void>;
  fetchTrade: (id: string) => Promise<void>;
  createTrade: (data: TradeCreate) => Promise<Trade>;
  updateTrade: (id: string, data: Partial<TradeCreate>) => Promise<Trade>;
  deleteTrade: (id: string) => Promise<void>;
  importTrades: (file: File, timezone: string, dryRun?: boolean) => Promise<any>;
  setCurrentTrade: (trade: Trade | null) => void;
  clearError: () => void;
}

export const useTradeStore = create<TradeStore>((set, get) => ({
  trades: [],
  currentTrade: null,
  loading: false,
  error: null,

  fetchTrades: async (filters) => {
    set({ loading: true, error: null });
    try {
      const trades = await tradeService.getAll(filters);
      set({ trades });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching trades' });
    } finally {
      set({ loading: false });
    }
  },

  fetchTradesByMonth: async (year: number, month: number) => {
    set({ loading: true, error: null });
    try {
      const trades = await tradeService.getByMonth(year, month);
      set({ trades });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching monthly trades' });
    } finally {
      set({ loading: false });
    }
  },

  fetchTrade: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const trade = await tradeService.getById(id);
      set({ currentTrade: trade });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching trade' });
    } finally {
      set({ loading: false });
    }
  },

  createTrade: async (data: TradeCreate) => {
    set({ loading: true, error: null });
    try {
      const newTrade = await tradeService.create(data);
      set((state) => ({
        trades: [...state.trades, newTrade],
      }));
      return newTrade;
    } catch (error: any) {
      set({ error: error.message || 'Error creating trade' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  updateTrade: async (id: string, data: Partial<TradeCreate>) => {
    set({ loading: true, error: null });
    try {
      const updated = await tradeService.update(id, data);
      set((state) => ({
        trades: state.trades.map((t) => (t.id === id ? updated : t)),
        currentTrade: state.currentTrade?.id === id ? updated : state.currentTrade,
      }));
      return updated;
    } catch (error: any) {
      set({ error: error.message || 'Error updating trade' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  deleteTrade: async (id: string) => {
    set({ loading: true, error: null });
    try {
      await tradeService.delete(id);
      set((state) => ({
        trades: state.trades.filter((t) => t.id !== id),
        currentTrade: state.currentTrade?.id === id ? null : state.currentTrade,
      }));
    } catch (error: any) {
      set({ error: error.message || 'Error deleting trade' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  importTrades: async (file: File, timezone: string, dryRun?: boolean) => {
    set({ loading: true, error: null });
    try {
      const result = await tradeService.importCSV(file, timezone, dryRun);
      if (!dryRun) {
        // Refresh trades after import
        await get().fetchTrades();
      }
      return result;
    } catch (error: any) {
      set({ error: error.message || 'Error importing trades' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  setCurrentTrade: (trade: Trade | null) => {
    set({ currentTrade: trade });
  },

  clearError: () => {
    set({ error: null });
  },
}));
