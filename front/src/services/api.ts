import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { User, Trade, Strategy, Watchlist, PerformanceData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    // Add token to requests if available
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle responses and errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(username: string, email: string, password: string): Promise<User> {
    const response = await this.api.post('/auth/register', { username, email, password });
    return response.data;
  }

  async login(username: string, password: string): Promise<{ access_token: string; refresh_token: string; token_type: string }> {
    const response = await this.api.post('/auth/login', { username, password });
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get('/users/me');
    return response.data;
  }

  // Trades endpoints
  async createTrade(trade: Partial<Trade>): Promise<Trade> {
    const response = await this.api.post('/trades', trade);
    return response.data;
  }

  async getTrades(skip = 0, limit = 100, filters?: any): Promise<Trade[]> {
    const response = await this.api.get('/trades', { params: { skip, limit, ...filters } });
    return response.data;
  }

  async getTrade(id: number): Promise<Trade> {
    const response = await this.api.get(`/trades/${id}`);
    return response.data;
  }

  async updateTrade(id: number, trade: Partial<Trade>): Promise<Trade> {
    const response = await this.api.put(`/trades/${id}`, trade);
    return response.data;
  }

  async deleteTrade(id: number): Promise<void> {
    await this.api.delete(`/trades/${id}`);
  }

  // Strategies endpoints
  async createStrategy(strategy: Partial<Strategy>): Promise<Strategy> {
    const response = await this.api.post('/strategies', strategy);
    return response.data;
  }

  async getStrategies(skip = 0, limit = 100): Promise<Strategy[]> {
    const response = await this.api.get('/strategies', { params: { skip, limit } });
    return response.data;
  }

  async getStrategy(id: number): Promise<Strategy> {
    const response = await this.api.get(`/strategies/${id}`);
    return response.data;
  }

  async updateStrategy(id: number, strategy: Partial<Strategy>): Promise<Strategy> {
    const response = await this.api.put(`/strategies/${id}`, strategy);
    return response.data;
  }

  async deleteStrategy(id: number): Promise<void> {
    await this.api.delete(`/strategies/${id}`);
  }

  // Watchlists endpoints
  async createWatchlist(watchlist: Partial<Watchlist>): Promise<Watchlist> {
    const response = await this.api.post('/watchlists', watchlist);
    return response.data;
  }

  async getWatchlists(skip = 0, limit = 100): Promise<Watchlist[]> {
    const response = await this.api.get('/watchlists', { params: { skip, limit } });
    return response.data;
  }

  async getWatchlist(id: number): Promise<Watchlist> {
    const response = await this.api.get(`/watchlists/${id}`);
    return response.data;
  }

  async updateWatchlist(id: number, watchlist: Partial<Watchlist>): Promise<Watchlist> {
    const response = await this.api.put(`/watchlists/${id}`, watchlist);
    return response.data;
  }

  async deleteWatchlist(id: number): Promise<void> {
    await this.api.delete(`/watchlists/${id}`);
  }

  // Performance endpoints
  async getPerformanceStats(filters?: any): Promise<PerformanceData> {
    const response = await this.api.get('/performance/stats', { params: filters });
    return response.data;
  }

  async getSymbolsPerformance(filters?: any): Promise<any> {
    const response = await this.api.get('/performance/symbols', { params: filters });
    return response.data;
  }
}

export default new ApiService();
