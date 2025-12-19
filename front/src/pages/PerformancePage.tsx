import React, { useEffect, useState } from 'react';
import { Card, LoadingSpinner } from '../components';
import apiService from '../services/api';
import type { PerformanceData } from '../types';

export const PerformancePage: React.FC = () => {
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPerformance = async () => {
      try {
        setLoading(true);
        const data = await apiService.getPerformanceStats();
        setPerformance(data);
      } catch (error) {
        console.error('Error loading performance:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPerformance();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (!performance) return <div className="text-center py-12">No performance data available</div>;

  const stats = performance.stats;
  const symbols = performance.best_worst_symbols;

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Performance Analysis</h1>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="text-center">
            <p className="text-gray-600 mb-2">Total P&L</p>
            <p className={`text-3xl font-bold ${stats.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${stats.total_pnl?.toFixed(2)}
            </p>
          </Card>
          <Card className="text-center">
            <p className="text-gray-600 mb-2">Win Rate</p>
            <p className="text-3xl font-bold text-blue-600">
              {((stats.win_rate || 0) * 100).toFixed(1)}%
            </p>
          </Card>
          <Card className="text-center">
            <p className="text-gray-600 mb-2">Winning Trades</p>
            <p className="text-3xl font-bold text-green-600">
              {stats.winning_trades}
            </p>
          </Card>
          <Card className="text-center">
            <p className="text-gray-600 mb-2">Losing Trades</p>
            <p className="text-3xl font-bold text-red-600">
              {stats.losing_trades}
            </p>
          </Card>
        </div>

        {/* Detailed Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card title="Detailed Statistics">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Average Win:</span>
                <span className="font-bold">${(stats.avg_win || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Average Loss:</span>
                <span className="font-bold">${(stats.avg_loss || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Largest Gain:</span>
                <span className="font-bold text-green-600">${(stats.largest_gain || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Largest Loss:</span>
                <span className="font-bold text-red-600">${(stats.largest_loss || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between border-t pt-3">
                <span className="text-gray-600">Risk/Reward Ratio:</span>
                <span className="font-bold">{(stats.risk_reward || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Profit Factor:</span>
                <span className="font-bold">{(stats.profit_factor || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Sharpe Ratio:</span>
                <span className="font-bold">{(stats.sharpe_ratio || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Max Drawdown:</span>
                <span className="font-bold">${(stats.max_drawdown || 0).toFixed(2)}</span>
              </div>
            </div>
          </Card>

          <Card title="Advanced Metrics">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Average Trade P&L:</span>
                <span className="font-bold">${(stats.avg_trade_pnl || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Median Trade P&L:</span>
                <span className="font-bold">${(stats.median_trade_pnl || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Max Consecutive Wins:</span>
                <span className="font-bold">{stats.max_consecutive_wins}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Max Consecutive Losses:</span>
                <span className="font-bold">{stats.max_consecutive_losses}</span>
              </div>
              <div className="flex justify-between border-t pt-3">
                <span className="text-gray-600">Avg Daily P&L:</span>
                <span className="font-bold">${(stats.avg_daily_pnl || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Trades Per Day:</span>
                <span className="font-bold">{(stats.avg_trades_per_day || 0).toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Daily Win Rate:</span>
                <span className="font-bold">
                  {((stats.daily_winrate || 0) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">SQN:</span>
                <span className="font-bold">{(stats.sqn || 0).toFixed(2)}</span>
              </div>
            </div>
          </Card>
        </div>

        {/* Best and Worst Symbols */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card title="Best Performing Symbols">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left">Symbol</th>
                    <th className="px-4 py-2 text-left">Trades</th>
                    <th className="px-4 py-2 text-left">Total P&L</th>
                    <th className="px-4 py-2 text-left">Win Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {symbols.best.map((symbol) => (
                    <tr key={symbol.symbol} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-bold">{symbol.symbol}</td>
                      <td className="px-4 py-2">{symbol.trade_count}</td>
                      <td className={`px-4 py-2 font-bold ${symbol.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${symbol.total_pnl.toFixed(2)}
                      </td>
                      <td className="px-4 py-2">
                        {((symbol.win_rate || 0) * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <Card title="Worst Performing Symbols">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left">Symbol</th>
                    <th className="px-4 py-2 text-left">Trades</th>
                    <th className="px-4 py-2 text-left">Total P&L</th>
                    <th className="px-4 py-2 text-left">Win Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {symbols.worst.map((symbol) => (
                    <tr key={symbol.symbol} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-bold">{symbol.symbol}</td>
                      <td className="px-4 py-2">{symbol.trade_count}</td>
                      <td className={`px-4 py-2 font-bold ${symbol.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${symbol.total_pnl.toFixed(2)}
                      </td>
                      <td className="px-4 py-2">
                        {((symbol.win_rate || 0) * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
