import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Card, LoadingSpinner } from '../components';
import apiService from '../services/api';
import type { Trade, Strategy, Watchlist, PerformanceData } from '../types';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [trades, setTrades] = useState<Trade[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [tradesData, strategiesData, watchlistsData, performanceData] = await Promise.all([
          apiService.getTrades(0, 5),
          apiService.getStrategies(0, 5),
          apiService.getWatchlists(0, 5),
          apiService.getPerformanceStats(),
        ]);

        setTrades(tradesData);
        setStrategies(strategiesData);
        setWatchlists(watchlistsData);
        setPerformance(performanceData);
      } catch (error) {
        console.error('Error loading dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Welcome, {user?.username}!</h1>

        {/* Performance Overview */}
        {performance && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card className="text-center">
              <p className="text-gray-600">Total P&L</p>
              <p className={`text-3xl font-bold ${performance.stats.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${performance.stats.total_pnl?.toFixed(2) || '0.00'}
              </p>
            </Card>
            <Card className="text-center">
              <p className="text-gray-600">Win Rate</p>
              <p className="text-3xl font-bold text-blue-600">
                {((performance.stats.win_rate || 0) * 100).toFixed(1)}%
              </p>
            </Card>
            <Card className="text-center">
              <p className="text-gray-600">Total Trades</p>
              <p className="text-3xl font-bold text-blue-600">
                {(performance.stats.winning_trades || 0) + (performance.stats.losing_trades || 0)}
              </p>
            </Card>
            <Card className="text-center">
              <p className="text-gray-600">Profit Factor</p>
              <p className="text-3xl font-bold text-blue-600">
                {(performance.stats.profit_factor || 0).toFixed(2)}
              </p>
            </Card>
          </div>
        )}

        {/* Recent Trades */}
        <Card title="Recent Trades" className="mb-8">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-2 text-left">Symbol</th>
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Entry Price</th>
                  <th className="px-4 py-2 text-left">Exit Price</th>
                  <th className="px-4 py-2 text-left">P&L</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => (
                  <tr key={trade.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2 font-bold">{trade.symbol}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded text-white text-sm ${trade.trade_type === 'LONG' ? 'bg-green-600' : 'bg-red-600'}`}>
                        {trade.trade_type}
                      </span>
                    </td>
                    <td className="px-4 py-2">${trade.entry_price?.toFixed(2)}</td>
                    <td className="px-4 py-2">${trade.exit_price?.toFixed(2) || '-'}</td>
                    <td className={`px-4 py-2 font-bold ${(trade.profit_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${(trade.profit_loss || 0).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Strategies and Watchlists */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card title={`Strategies (${strategies.length})`}>
            <ul className="space-y-2">
              {strategies.map((strategy) => (
                <li key={strategy.id} className="p-3 bg-gray-50 rounded">
                  <p className="font-bold">{strategy.name}</p>
                  <p className="text-sm text-gray-600">{strategy.description}</p>
                </li>
              ))}
            </ul>
          </Card>

          <Card title={`Watchlists (${watchlists.length})`}>
            <ul className="space-y-2">
              {watchlists.map((watchlist) => (
                <li key={watchlist.id} className="p-3 bg-gray-50 rounded">
                  <p className="font-bold">{watchlist.name}</p>
                  <p className="text-sm text-gray-600">{watchlist.entries?.length || 0} entries</p>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
};
