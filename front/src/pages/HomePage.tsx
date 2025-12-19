import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { StatsCard } from '../components';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-bg to-card-bg text-text-primary">
        <div className="max-w-7xl mx-auto px-4 py-20">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">Trading Journal</h1>
            <p className="text-xl mb-12 max-w-2xl mx-auto text-text-muted">
              Track your trades, analyze your performance, and improve your trading discipline with our comprehensive trading journal application.
            </p>

            <div className="flex gap-4 justify-center mb-16">
              <button
                onClick={() => navigate('/login')}
                className="px-8 py-3 bg-primary text-white rounded-pill font-semibold hover:opacity-90 transition-opacity"
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/register')}
                className="px-8 py-3 bg-secondary text-white rounded-pill font-semibold hover:opacity-90 transition-opacity"
              >
                Create Account
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg text-text-primary">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold">Welcome to Trading Journal</h1>
          <p className="text-text-muted text-lg mt-2">Manage your trading activities and analyze your performance</p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
          <StatsCard
            icon="eye"
            title="Watchlist"
            description="Manage your daily monitored assets"
            onClick={() => navigate('/watchlists')}
          />
          <StatsCard
            icon="book"
            title="Trading Journal"
            description="Record and analyze all your trades"
            onClick={() => navigate('/trades')}
          />
          <StatsCard
            icon="chart-bar"
            title="Performance"
            description="Analyze your trading performance metrics"
            onClick={() => navigate('/performance')}
          />
          <StatsCard
            icon="lightbulb"
            title="Improvements"
            description="Track your trading improvements and errors"
            onClick={() => navigate('/')}
          />
          <StatsCard
            icon="cog"
            title="Strategies"
            description="Manage your trading strategies"
            onClick={() => navigate('/strategies')}
          />
          <StatsCard
            icon="search"
            title="Screeners"
            description="Find trading opportunities with screeners"
            onClick={() => navigate('/')}
          />
          <StatsCard
            icon="chart-pie"
            title="Assets"
            description="Manage your trading assets"
            onClick={() => navigate('/')}
          />
          <StatsCard
            icon="sliders-h"
            title="Settings"
            description="Customize your preferences"
            onClick={() => navigate('/')}
          />
        </div>
      </div>
    </div>
  );
};
