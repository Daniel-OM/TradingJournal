import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, LoadingSpinner, Button } from '../components';
import apiService from '../services/api';
import type { Strategy } from '../types';

export const StrategiesPage: React.FC = () => {
  const navigate = useNavigate();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStrategies = async () => {
      try {
        setLoading(true);
        const data = await apiService.getStrategies();
        setStrategies(data);
      } catch (error) {
        console.error('Error loading strategies:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStrategies();
  }, []);

  const handleDeleteStrategy = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this strategy?')) {
      try {
        await apiService.deleteStrategy(id);
        setStrategies(strategies.filter((s) => s.id !== id));
      } catch (error) {
        console.error('Error deleting strategy:', error);
      }
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">Strategies</h1>
          <Button onClick={() => navigate('/strategies/new')} variant="primary">
            New Strategy
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategies.map((strategy) => (
            <Card key={strategy.id} className="flex flex-col">
              <h3 className="text-2xl font-bold mb-2">{strategy.name}</h3>
              <p className="text-gray-600 mb-4 flex-grow">{strategy.description}</p>
              <p className="text-sm text-gray-500 mb-4">
                {strategy.conditions?.length || 0} conditions
              </p>
              <div className={`mb-4 inline-block px-3 py-1 rounded text-white text-sm ${strategy.is_active ? 'bg-green-600' : 'bg-gray-600'}`}>
                {strategy.is_active ? 'Active' : 'Inactive'}
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => navigate(`/strategies/${strategy.id}`)}
                  variant="secondary"
                  className="flex-1"
                >
                  View
                </Button>
                <Button
                  onClick={() => navigate(`/strategies/${strategy.id}/edit`)}
                  variant="secondary"
                  className="flex-1"
                >
                  Edit
                </Button>
                <Button
                  onClick={() => handleDeleteStrategy(strategy.id)}
                  variant="danger"
                  className="flex-1"
                >
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {strategies.length === 0 && (
          <Card className="text-center py-12">
            <p className="text-gray-600 mb-4">No strategies yet</p>
            <Button onClick={() => navigate('/strategies/new')} variant="primary">
              Create your first strategy
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
};
