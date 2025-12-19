import { create } from 'zustand';
import type { Watchlist, WatchlistCreate, WatchlistEntry, WatchlistEntryCreate } from '../types/api';
import { watchlistService } from '../services/watchlistService';

interface WatchlistStore {
  watchlists: Watchlist[];
  currentWatchlist: Watchlist | null;
  currentEntries: WatchlistEntry[];
  loading: boolean;
  error: string | null;

  fetchWatchlists: () => Promise<void>;
  fetchWatchlist: (id: string) => Promise<void>;
  fetchWatchlistEntries: (watchlistId: string) => Promise<void>;
  createWatchlist: (data: WatchlistCreate) => Promise<Watchlist>;
  updateWatchlist: (id: string, data: Partial<WatchlistCreate>) => Promise<Watchlist>;
  deleteWatchlist: (id: string) => Promise<void>;
  addEntry: (watchlistId: string, data: WatchlistEntryCreate) => Promise<WatchlistEntry>;
  updateEntry: (watchlistId: string, entryId: string, data: Partial<WatchlistEntryCreate>) => Promise<WatchlistEntry>;
  deleteEntry: (watchlistId: string, entryId: string) => Promise<void>;
  setCurrentWatchlist: (watchlist: Watchlist | null) => void;
  clearError: () => void;
}

export const useWatchlistStore = create<WatchlistStore>((set) => ({
  watchlists: [],
  currentWatchlist: null,
  currentEntries: [],
  loading: false,
  error: null,

  fetchWatchlists: async () => {
    set({ loading: true, error: null });
    try {
      const watchlists = await watchlistService.getAll();
      set({ watchlists });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching watchlists' });
    } finally {
      set({ loading: false });
    }
  },

  fetchWatchlist: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const watchlist = await watchlistService.getById(id);
      set({ currentWatchlist: watchlist });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching watchlist' });
    } finally {
      set({ loading: false });
    }
  },

  fetchWatchlistEntries: async (watchlistId: string) => {
    set({ loading: true, error: null });
    try {
      const entries = await watchlistService.getEntries(watchlistId);
      set({ currentEntries: entries });
    } catch (error: any) {
      set({ error: error.message || 'Error fetching watchlist entries' });
    } finally {
      set({ loading: false });
    }
  },

  createWatchlist: async (data: WatchlistCreate) => {
    set({ loading: true, error: null });
    try {
      const newWatchlist = await watchlistService.create(data);
      set((state) => ({
        watchlists: [...state.watchlists, newWatchlist],
      }));
      return newWatchlist;
    } catch (error: any) {
      set({ error: error.message || 'Error creating watchlist' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  updateWatchlist: async (id: string, data: Partial<WatchlistCreate>) => {
    set({ loading: true, error: null });
    try {
      const updated = await watchlistService.update(id, data);
      set((state) => ({
        watchlists: state.watchlists.map((w) => (w.id === id ? updated : w)),
        currentWatchlist: state.currentWatchlist?.id === id ? updated : state.currentWatchlist,
      }));
      return updated;
    } catch (error: any) {
      set({ error: error.message || 'Error updating watchlist' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  deleteWatchlist: async (id: string) => {
    set({ loading: true, error: null });
    try {
      await watchlistService.delete(id);
      set((state) => ({
        watchlists: state.watchlists.filter((w) => w.id !== id),
        currentWatchlist: state.currentWatchlist?.id === id ? null : state.currentWatchlist,
      }));
    } catch (error: any) {
      set({ error: error.message || 'Error deleting watchlist' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  addEntry: async (watchlistId: string, data: WatchlistEntryCreate) => {
    set({ loading: true, error: null });
    try {
      const newEntry = await watchlistService.addEntry(watchlistId, data);
      set((state) => ({
        currentEntries: [...state.currentEntries, newEntry],
      }));
      return newEntry;
    } catch (error: any) {
      set({ error: error.message || 'Error adding entry' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  updateEntry: async (watchlistId: string, entryId: string, data: Partial<WatchlistEntryCreate>) => {
    set({ loading: true, error: null });
    try {
      const updated = await watchlistService.updateEntry(watchlistId, entryId, data);
      set((state) => ({
        currentEntries: state.currentEntries.map((e) => (e.id === entryId ? updated : e)),
      }));
      return updated;
    } catch (error: any) {
      set({ error: error.message || 'Error updating entry' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  deleteEntry: async (watchlistId: string, entryId: string) => {
    set({ loading: true, error: null });
    try {
      await watchlistService.deleteEntry(watchlistId, entryId);
      set((state) => ({
        currentEntries: state.currentEntries.filter((e) => e.id !== entryId),
      }));
    } catch (error: any) {
      set({ error: error.message || 'Error deleting entry' });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  setCurrentWatchlist: (watchlist: Watchlist | null) => {
    set({ currentWatchlist: watchlist });
  },

  clearError: () => {
    set({ error: null });
  },
}));
